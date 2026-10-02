"""Local/manual training gate. No submission, authentication, or authenticity guarantee.

Drafts refuse execution. A trusted operator must review the exact evidence and call
admit immediately before submission. Runtime repeats checks before any bootstrap.
Submitting a blocked draft can still incur provider startup charges.
"""
import copy
import functools
import hashlib
import inspect
import json
from pathlib import Path, PurePosixPath
import re

GROUPS = {'data', 'checkpoint_model', 'prompts', 'benchmark_qualification',
          'diagnostic_qualification', 'actual_exposure', 'objective_optimizer_sampling',
          'runtime_code', 'limits'}
BLOCKED = "raise ValueError('Training blocked: completed acquisition, exact contract, Astra review and human job authorization required')\n"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    try:
        return json.loads(path.read_text('utf-8'), object_pairs_hook=unique,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError('Missing or invalid admission evidence: ' + str(path)) from error


def fields(record, expected):
    if type(record) is not dict or set(record) != set(expected):
        raise ValueError('Unexpected admission schema')


def text(value):
    if type(value) is not str or not value.strip():
        raise ValueError('Nonempty evidence text required')


def sha(value):
    if type(value) is not str or not re.fullmatch('[a-f0-9]{64}', value):
        raise ValueError('Exact SHA-256 required')


def artifact(root, record):
    fields(record, {'path', 'sha256', 'bytes'})
    name = record['path']
    text(name)
    sha(record['sha256'])
    if ('\\' in name or ':' in name or PurePosixPath(name).is_absolute()
            or any(p in {'', '.', '..'} for p in name.split('/'))
            or type(record['bytes']) is not int or record['bytes'] < 1):
        raise ValueError('Unsafe artifact path or byte count')
    path = root / name
    if (not path.resolve().is_relative_to(root.resolve())
            or any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root))
            or not path.is_file() or path.stat().st_size != record['bytes']
            or digest(path.read_bytes()) != record['sha256']):
        raise ValueError('Changed or missing evidence artifact: ' + name)
    return path


def validate(root, job_sha256, contract_sha256=None, receipt_sha256=None):
    """Verify manual records and exact bytes, not reviewer/human authenticity."""
    root = Path(root)
    sha(job_sha256)
    if receipt_sha256 is not None and digest((root / 'training-admission.json').read_bytes()) != receipt_sha256:
        raise ValueError('Approved admission receipt changed')
    receipt = read_json(root / 'training-admission.json')
    fields(receipt, {'schema_version', 'contract', 'acquisition', 'decision', 'validation', 'review', 'authorization'})
    if type(receipt['schema_version']) is not int or receipt['schema_version'] != 1:
        raise ValueError('Admission schema version differs')
    paths = {name: artifact(root, receipt[name]) for name in receipt if name != 'schema_version'}
    if contract_sha256 is not None and receipt['contract']['sha256'] != contract_sha256:
        raise ValueError('Approved contract changed')
    contract = read_json(paths['contract'])
    fields(contract, {'schema_version', 'job_sha256', 'experiment_id', 'execution_owner', 'job', 'artifacts', 'acquisition'})
    if type(contract['schema_version']) is not int or contract['schema_version'] != 1:
        raise ValueError('Contract schema version differs')
    text(contract['experiment_id'])
    text(contract['execution_owner'])
    if contract['job_sha256'] != job_sha256 or digest(canonical(contract['job'])) != job_sha256:
        raise ValueError('Exact job/settings/code contract differs')
    fields(contract['artifacts'], GROUPS)
    for records in contract['artifacts'].values():
        if type(records) is not list or not records:
            raise ValueError('Each scientific contract category requires exact artifacts')
        for record in records:
            artifact(root, record)
    contract_hash = receipt['contract']['sha256']
    fields(contract['acquisition'], {'packet_sha256', 'expected_outputs'})
    sha(contract['acquisition']['packet_sha256'])
    if type(contract['acquisition']['expected_outputs']) is not int or contract['acquisition']['expected_outputs'] < 1:
        raise ValueError('Frozen acquisition schedule required')
    acquisition = read_json(paths['acquisition'])
    fields(acquisition, {'status', 'packet_sha256', 'expected_outputs', 'completed_outputs', 'results'})
    sha(acquisition['packet_sha256'])
    if (acquisition['status'] != 'completed' or type(acquisition['expected_outputs']) is not int
            or acquisition['expected_outputs'] < 1 or type(acquisition['completed_outputs']) is not int
            or acquisition['completed_outputs'] != acquisition['expected_outputs']
            or acquisition['expected_outputs'] != contract['acquisition']['expected_outputs']
            or acquisition['packet_sha256'] != contract['acquisition']['packet_sha256']):
        raise ValueError('Acquisition diagnostic incomplete')
    artifact(root, acquisition['results'])
    if acquisition['packet_sha256'] not in {r['sha256'] for r in contract['artifacts']['diagnostic_qualification']}:
        raise ValueError('Acquisition packet differs from qualified contract')
    decision = read_json(paths['decision'])
    fields(decision, {'contract_sha256', 'acquisition_sha256', 'status', 'rationale'})
    text(decision['rationale'])
    if (decision['status'] != 'training_justified' or decision['contract_sha256'] != contract_hash
            or decision['acquisition_sha256'] != receipt['acquisition']['sha256']):
        raise ValueError('Reasoned scientific training decision missing')
    validation = read_json(paths['validation'])
    fields(validation, {'contract_sha256', 'status', 'checks'})
    if validation['status'] != 'PASS' or validation['contract_sha256'] != contract_hash:
        raise ValueError('Validation did not pass exact contract')
    if type(validation['checks']) is not list or not validation['checks']:
        raise ValueError('Validation check evidence missing')
    for record in validation['checks']:
        artifact(root, record)
    review = read_json(paths['review'])
    fields(review, {'contract_sha256', 'acquisition_sha256', 'decision_sha256', 'validation_sha256',
                    'status', 'model', 'reviewer_id', 'implementer_id', 'rationale'})
    for name in ('reviewer_id', 'implementer_id', 'rationale'):
        text(review[name])
    if (review['status'] != 'APPROVE' or review['model'] != 'gpt-6-astra'
            or review['reviewer_id'] == review['implementer_id']
            or review['contract_sha256'] != contract_hash
            or any(review[name + '_sha256'] != receipt[name]['sha256'] for name in ('acquisition', 'decision', 'validation'))):
        raise ValueError('Distinct Astra approval of exact evidence missing')
    authorization = read_json(paths['authorization'])
    fields(authorization, {'status', 'human', 'job_sha256', 'contract_sha256', 'review_sha256', 'execution_owner', 'exact_action'})
    for name in ('human', 'exact_action'):
        text(authorization[name])
    if (authorization['status'] != 'AUTHORIZE_TRAINING_JOB'
            or authorization['job_sha256'] != job_sha256 or authorization['contract_sha256'] != contract_hash
            or authorization['execution_owner'] != contract['execution_owner']
            or authorization['review_sha256'] != receipt['review']['sha256']):
        raise ValueError('Explicit human authorization of exact reviewed job missing')
    return receipt


def plain(value):
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(item) for item in value]
    if hasattr(value, 'to_dict'):
        return plain(value.to_dict())
    return value


def draft(builder):
    """Protect every maintained builder; inspect intended_command for offline tests."""
    @functools.wraps(builder)
    def prepare(*args, **kwargs):
        spec, provenance = builder(*args, **kwargs)
        job = plain({'spec': spec, 'provenance': provenance})
        intended = spec['command'][3]
        spec['command'][3] = BLOCKED + intended
        provenance = dict(provenance, training_admission={
            'status': 'BLOCKED_DRAFT', 'job': job, 'job_sha256': digest(canonical(job)),
            'intended_command': intended, 'intended_command_sha256': digest(intended.encode())})
        provenance['command_sha256'] = digest(spec['command'][3].encode())
        return spec, provenance
    return prepare


def admit(spec, preparation, evidence_root):
    """Local pre-submission gate. Call immediately before the external submitter.

    Copies the spec and repeats checks in /input/training-admission/<job hash>.
    The operator must manually verify reviewer identity and human authorization.
    """
    gate = preparation['training_admission']
    fields(gate, {'status', 'job', 'job_sha256', 'intended_command', 'intended_command_sha256'})
    if gate['status'] != 'BLOCKED_DRAFT':
        raise ValueError('Expected immutable blocked draft')
    job = copy.deepcopy(gate['job'])
    if (digest(canonical(job)) != gate['job_sha256']
            or digest(gate['intended_command'].encode()) != gate['intended_command_sha256']
            or job['spec']['command'][3] != gate['intended_command']):
        raise ValueError('Draft preparation changed')
    expected = copy.deepcopy(job['spec'])
    expected['command'][3] = BLOCKED + gate['intended_command']
    if plain(spec) != expected:
        raise ValueError('Draft spec changed')
    metadata = {k: v for k, v in preparation.items() if k != 'training_admission'}
    metadata['command_sha256'] = gate['intended_command_sha256']
    if metadata != job['provenance']:
        raise ValueError('Draft settings/provenance changed')
    receipt = validate(evidence_root, gate['job_sha256'])
    source = 'import hashlib,json,re\nfrom pathlib import Path,PurePosixPath\nGROUPS = ' + repr(GROUPS) + '\n'
    for function in (canonical, digest, unique, read_json, fields, text, sha, artifact, validate):
        source += inspect.getsource(function) + '\n'
    source += 'validate(' + repr('/input/training-admission/' + gate['job_sha256']) + ', ' + repr(gate['job_sha256']) + ', ' + repr(receipt['contract']['sha256']) + ', ' + repr(digest((Path(evidence_root) / 'training-admission.json').read_bytes())) + ')\n'
    result = copy.deepcopy(spec)
    result['command'][3] = source + gate['intended_command']
    if any(len(s.encode()) + 1 >= 100 * 1024 for s in result['command']):
        raise ValueError('Admitted runtime guard exceeds argument limit')
    compile(result['command'][3], 'admitted-training', 'exec')
    return result


def sdk_spec(spec):
    """Rebuild saved volumes and exercise the installed, pure SDK boundary."""
    from huggingface_hub import HfApi, Volume
    from huggingface_hub.hf_api import _create_job_spec

    result = copy.deepcopy(spec)
    if 'volumes' in result:
        if type(result['volumes']) is not list:
            raise ValueError('SDK volumes must be a list')
        volumes = []
        for volume in result['volumes']:
            if type(volume) not in (dict, Volume):
                raise ValueError('Unsupported SDK volume representation')
            record = volume if type(volume) is dict else volume.to_dict()
            required = {'type', 'source', 'mountPath'}
            if (not required <= set(record)
                    or set(record) - (required | {'revision', 'readOnly', 'path'})):
                raise ValueError('Unexpected SDK volume schema')
            if record['type'] not in ('bucket', 'model', 'dataset', 'space'):
                raise ValueError('Unsupported SDK volume type')
            for name in ('type', 'source', 'mountPath', 'revision', 'path'):
                if name in record:
                    text(record[name])
            if (not record['mountPath'].startswith('/')
                    or ('readOnly' in record and type(record['readOnly']) is not bool)):
                raise ValueError('Invalid SDK volume mount or readOnly')
            native = Volume(**record)
            if native.to_dict() != record:
                raise ValueError('SDK volume reconstruction changed settings')
            volumes.append(native)
        result['volumes'] = volumes
    try:
        arguments = inspect.signature(HfApi.run_job).bind(None, **result)
        arguments.apply_defaults()
        payload = dict(arguments.arguments)
        for name in ('self', 'namespace', 'token'):
            payload.pop(name)
        canonical(_create_job_spec(**payload))
    except (TypeError, ValueError, AttributeError, IndexError) as error:
        raise ValueError('Job cannot serialize through installed SDK') from error
    return result


def submit(api, spec, preparation, evidence_root):
    """One owner, one submission attempt; retain claim on unknown/failure.

    After an unknown result, inspect the provider before manual recovery. Never
    automatically remove a claim or retry. api must be provided by the operator.
    """
    admitted = sdk_spec(admit(spec, preparation, evidence_root))
    root = Path(evidence_root)
    gate = preparation['training_admission']
    receipt = validate(root, gate['job_sha256'])
    identity = dict(job_sha256=gate['job_sha256'],
        admission_receipt_sha256=digest((root / 'training-admission.json').read_bytes()),
        contract_sha256=receipt['contract']['sha256'],
        command_sha256=digest(admitted['command'][3].encode()),
        spec_sha256=digest(canonical(plain(admitted))),
        status='SUBMISSION_CLAIMED_OUTCOME_UNKNOWN_CHECK_PROVIDER_BEFORE_RECOVERY')
    claim = root / ('submission-' + gate['job_sha256'] + '.json')
    try:
        with claim.open('xb') as stream:
            stream.write(canonical(identity))
    except FileExistsError as error:
        raise ValueError('Submission already claimed; inspect provider before manual recovery') from error
    # Final evidence check immediately before the single API call.
    validate(root, gate['job_sha256'], receipt['contract']['sha256'], identity['admission_receipt_sha256'])
    return api.run_job(**admitted)
