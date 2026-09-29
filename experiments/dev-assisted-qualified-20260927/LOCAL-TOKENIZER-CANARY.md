# Local tokenizer and native Qwen CPU canary

27 September 2026. **PASS within the local scope below.** No network, cloud job, checkpoint loading, package installation or credential access was performed. Existing installed packages were composed only inside isolated subprocesses; neither environment was modified.

## Actual imported packages

| Package | Version | Loaded module |
| --- | --- | --- |
| torch | 2.11.0+cu128 | `[USER_HOME]\.venvs\codex-science\Lib\site-packages\torch\__init__.py` |
| transformers | 5.13.1 | `[USER_HOME]\.venvs\codex-science\Lib\site-packages\transformers\__init__.py` |
| huggingface_hub | 1.23.0 | `[USER_HOME]\Documents\ChatGPT\Pahlavi language\resources\local\hf-client-venv\Lib\site-packages\huggingface_hub\__init__.py` |
| tokenizers | 0.22.2 | `[USER_HOME]\.venvs\codex-science\Lib\site-packages\tokenizers\__init__.py` |
| jinja2 | 3.1.6 | `[USER_HOME]\.venvs\codex-science\Lib\site-packages\jinja2\__init__.py` |

The science interpreter retains precedence. The only added search path is the existing project `resources/local/hf-client-venv/Lib/site-packages`, appended after the interpreter defaults. Offline and telemetry-disable flags apply only to these subprocesses.

## Exact Gemma prompt lengths

Loaded the local official `GemmaTokenizer` using `AutoTokenizer.from_pretrained(..., local_files_only=True, trust_remote_code=False)`. Used the unchanged `dev_assisted.messages` function, source-only DEV inputs, and hash-checked frozen evidence/audit. Actual `apply_chat_template` arguments: `tokenize=True, return_dict=False, add_generation_prompt=True, enable_thinking=False`. No truncation or manual token estimation. These are **Gemma token lengths**, not Qwen lengths.

- plain: n=24, min=182, median=248, mean=259.625, max=456.
- assisted: n=24, min=1273, median=3621, mean=3101.542, max=4142.

Longest prompt: `QUALITYDEV1-024:assisted`, **4,142 tokens**. Adding the unchanged 4,096-token output ceiling gives **8,238 total tokens**. This establishes tokenizer size only, not GPU fit, latency or quality.

| Case | Plain tokens | Assisted tokens |
| --- | ---: | ---: |
| QUALITYDEV1-001 | 182 | 1273 |
| QUALITYDEV1-002 | 185 | 3409 |
| QUALITYDEV1-003 | 190 | 1337 |
| QUALITYDEV1-004 | 189 | 2298 |
| QUALITYDEV1-005 | 198 | 3870 |
| QUALITYDEV1-006 | 277 | 2814 |
| QUALITYDEV1-007 | 192 | 2545 |
| QUALITYDEV1-008 | 217 | 3539 |
| QUALITYDEV1-009 | 222 | 3765 |
| QUALITYDEV1-010 | 247 | 4005 |
| QUALITYDEV1-011 | 297 | 3772 |
| QUALITYDEV1-012 | 359 | 3941 |
| QUALITYDEV1-013 | 204 | 3714 |
| QUALITYDEV1-014 | 227 | 3717 |
| QUALITYDEV1-015 | 249 | 2694 |
| QUALITYDEV1-016 | 256 | 2605 |
| QUALITYDEV1-017 | 275 | 1500 |
| QUALITYDEV1-018 | 288 | 3703 |
| QUALITYDEV1-019 | 228 | 2516 |
| QUALITYDEV1-020 | 257 | 3790 |
| QUALITYDEV1-021 | 291 | 3889 |
| QUALITYDEV1-022 | 345 | 4051 |
| QUALITYDEV1-023 | 400 | 1548 |
| QUALITYDEV1-024 | 456 | 4142 |

### Rendered input-token identities

SHA256 uses the existing canonical JSON serialization of each complete integer token-ID list.

| Case/condition | Input IDs SHA256 |
| --- | --- |
| QUALITYDEV1-001:plain | `2727e3513cf5392c9de4ae92101c39b982afca5987d305ee996b840028803fe4` |
| QUALITYDEV1-001:assisted | `40b983dc0500b8462be05975e760da707c82abec40dbb38027d38148b334c0a2` |
| QUALITYDEV1-002:plain | `04d59898680a5390ff5074dc78b41215780c4863a7386a9d6f5b09a23667d028` |
| QUALITYDEV1-002:assisted | `94cfc49268e705c9b96b79abd794df139f0394abd1308949ffa773cb5297256e` |
| QUALITYDEV1-003:plain | `d096289270f6902729266996e5597f42aa64ff6c087f0a7303527565d8b0f402` |
| QUALITYDEV1-003:assisted | `e27fc6a674b7ee58572170751b6eb3e9ec37f710f503b02fa65d0084786ce793` |
| QUALITYDEV1-004:plain | `375de30cb2bc9549346bc2d4c3cbab98ca03fcb5c509fb000847f9d0da6e6563` |
| QUALITYDEV1-004:assisted | `3b8aa3de4fd9d475643fc4e6f4e3116ba12b55b991926af7e6d509017cd636b8` |
| QUALITYDEV1-005:plain | `ae11f5ba28c2f90932185af64371d138d7ce0b60512df12f0d46aea186a1deaa` |
| QUALITYDEV1-005:assisted | `ed2baf8a1b29675577582663b4aa54e21e83878dd5409e92e6c51fb0f7cfc100` |
| QUALITYDEV1-006:plain | `0edb2c1719349b64409a05dce836cec96dc9e302bbc7928dc56b27a81cf4a337` |
| QUALITYDEV1-006:assisted | `a5a60bfd6cce2746c74f51634e46141b99759bc56c6f6d5ce6e0f5192cd91c64` |
| QUALITYDEV1-007:plain | `15d5a762f8aa7f0c08515b0be5ca9104b187a8046ee95d50a9d9c26b51b4ab92` |
| QUALITYDEV1-007:assisted | `b036be9481120e68c0bb78f91cde071bc939e053d4d5296e0834b78f74f70236` |
| QUALITYDEV1-008:plain | `0b8e6020a7c4fc6f722dd6e07b18a4a0d1f4b27631dbf4dc69e086d8cc839d88` |
| QUALITYDEV1-008:assisted | `6f3a25d1c27e7990f716020ee57730c6f51b1f952285dc0996b8a53a61612762` |
| QUALITYDEV1-009:plain | `ca92d96668f973dca591acc99d00b9ee2bc668cc5e7eca7b9a34d4cc15ad5a52` |
| QUALITYDEV1-009:assisted | `ecd41f1b874ee6bdaefcf7a3749d2b65b5206c136574c54fd9a3ef9e8f9b658e` |
| QUALITYDEV1-010:plain | `0a8482e3a4fe8066ed8c18677da91a29fb4a04544110cc7a41d30ac4822e2cdf` |
| QUALITYDEV1-010:assisted | `9d90a26f9dbc1244de100e6c13ad903d5ae7175bb5225446b534d4ac282bc12b` |
| QUALITYDEV1-011:plain | `7f577d46557305de4c10e4b9c082230add8a9f6557a1040c5a8483bb8c6975c0` |
| QUALITYDEV1-011:assisted | `b2f0384be87ac4cd42f72a666868c1d660887f445d2542fa986952eda43e12f8` |
| QUALITYDEV1-012:plain | `3721e1c69420ac896e222411a119da30a33a2a10d909bff0afb55e8d306d8d0d` |
| QUALITYDEV1-012:assisted | `c4d420b768807304a064bb39eacf7953b96d7ec00c27259828498240532e3d7d` |
| QUALITYDEV1-013:plain | `8e1c1f8942571371fe5225e929321287fbee856beea0efc16fb2420367ccdc57` |
| QUALITYDEV1-013:assisted | `c2234ebd1e87b8fd36747754dc388ce307ee65506e1a658cadeb5c7298fe03e4` |
| QUALITYDEV1-014:plain | `3b5dc8535532d60b72885cba6eae71d6e2ca2a201d2e84370813f0cb3e0eaedf` |
| QUALITYDEV1-014:assisted | `08df58e68f679c40ea4a5b12bc9b72815db9544be0bf50b2d62b22fb7823073a` |
| QUALITYDEV1-015:plain | `0f42b3c0b22e447378e9785f276dbb83829ebe4b92a79c4f49a00a63803a5a83` |
| QUALITYDEV1-015:assisted | `2f667dc031e6fdc85368b8d9c21a882da10b53671f1d308b5c4cd5513f02df6a` |
| QUALITYDEV1-016:plain | `d095e448fc3c891172d2d2a9319c84229eb82fb4abce196b5d421e648f5f4555` |
| QUALITYDEV1-016:assisted | `f10ac5565919c9368f23d78246c841c4af94db6d33c6cb3d51bb402ea1cbd450` |
| QUALITYDEV1-017:plain | `26d97730773bf5656e19ddcb1ec7e8eae6b22137e3f0ab6fc27937a93f4f95f0` |
| QUALITYDEV1-017:assisted | `0c9f2d805a4f6742caa32bd03f26562fd53029056e010e76ce82e05372853174` |
| QUALITYDEV1-018:plain | `5db5b015088e0f3a48dd091d388ce155ba085e2680d0284cd2d1ba91181a9f3a` |
| QUALITYDEV1-018:assisted | `f8a86bacec1bd4c8659a9cc15025e5f58fc6bfc5066a7e1ed7936b9ed001edc7` |
| QUALITYDEV1-019:plain | `2815c480b2ce22990aa5be52afdc99a493518b79f2b2b98b72cb3a5d2b779572` |
| QUALITYDEV1-019:assisted | `e055a71befeee6966a379817a1a975201670710f1528b97640248db03c6a85b9` |
| QUALITYDEV1-020:plain | `157e4cd8809392a6c062d81366574fb80a5d39a31fbece181c53a993d4415903` |
| QUALITYDEV1-020:assisted | `b7d595b2798f7fe78acec7af3cc9bb8db99f9494f7aa4fe5fba1c18b035ab191` |
| QUALITYDEV1-021:plain | `f04c9e5dc2f735a6f7d75f859879ad1074d0acbbc888bcfdcb6417e7a58341f4` |
| QUALITYDEV1-021:assisted | `52873da5c4664a35d2f9699f4a1477395f94bdf7f8c958c794b5c1c7bb4ffe76` |
| QUALITYDEV1-022:plain | `46d521c5056d9bf7a4be8a17d0f17a1cb714f6f68bfe910540326841e3219c2d` |
| QUALITYDEV1-022:assisted | `45de062cd44c29a41c286c055161616517c76191a01d469dcff536a265b4036e` |
| QUALITYDEV1-023:plain | `f7bac0e54791acc5184e2ebb9e4768333962574388907667e182f279e1136143` |
| QUALITYDEV1-023:assisted | `803f4960a17ba35243d1fc3f755cde4e49649968f1048f24e6eb00fb065f76fb` |
| QUALITYDEV1-024:plain | `78f82faed8ce2c6439d69f8261c5654d5f7215e7e00961949539483214f79254` |
| QUALITYDEV1-024:assisted | `6464e1ccc5b9fe25a01b77f07cc51ae7356814b04bb74e720013114d87c3440f` |

### Local input identities

| File | SHA256 |
| --- | --- |
| `cloud_pilot/dev_assisted.py` | `f26e8c29ab1b3390455f6a93e2ea34cb44f3ff6d627f4957de583a737c884940` |
| `cloud_pilot/dev_diagnostic.py` | `9d459482f3b7189cc2109bd68e36d14e77693df64f41574ff952d71bc6725d11` |
| `cloud_pilot/palref_eval.py` | `050a38880c68113ca5e5ebc4abd26945d05959eeda52f5df64f00292acfe4a49` |
| `experiments/dev-diagnostic-20260927/inputs.jsonl` | `06ac58310bf67767fae4124d8e935c808d15debcd8daebce07b583937cd97182` |
| `experiments/dev-assisted-qualified-20260927/evidence/evidence.jsonl` | `1d5e02cfb91dad1da94db072e9f5fcd6be463746bbc951425cb6631b5ea2ce4a` |
| `experiments/dev-assisted-qualified-20260927/evidence/audit.json` | `193f49f54dd1649a6a0002ed423bdf3dfa7176a7a093e1532cdd1ce1ea32d8f1` |
| `resources/local/cloud-pilot-qualified-20260927/tokenizer/chat_template.jinja` | `ae53464bf3be25802b3a5b37def7fd89667067d7577049b3b2d74c4d8de4c6d4` |
| `resources/local/cloud-pilot-qualified-20260927/tokenizer/tokenizer.json` | `cc8d3a0ce36466ccc1278bf987df5f71db1719b9ca6b4118264f45cb627bfe0f` |
| `resources/local/cloud-pilot-qualified-20260927/tokenizer/tokenizer_config.json` | `9f4fec4b1dc6ecddf8f4a92e9caea5971c0e67d81309f3f9066a2bee8c362633` |

## Native random-model canary

Executed `cloud_pilot/check_qwen_native.py` against real Transformers5.13.1 and Torch2.11.0+cu128 on CPU. The model has **18,428 random parameters**, vocabulary32, hidden32, and two layers: one linear-attention layer and one full-attention layer. It used the native Torch fallback because optional acceleration packages are absent.

- Actual `generate` accepted the custom presence callable and `use_cache=True, logits_to_keep=1`.
- At all three generated steps, returned processed scores matched the independently constructed native processor list: presence, temperature0.7, top_k20, top_p0.8, min_p0. Repetition penalty remained1.0.
- Generated full sequence: `[1,2,3,4,25,5,24]`. Repeating generation with seed42 returned the same sequence.
- Native `DynamicCache` was returned; cache sequence length6 equals prompt4 plus two cached decode inputs.
- No subclasses, dependency stubs, source extraction, model downloads or checkpoint weights were used.

Exact tested command, from the project root:

```powershell
& '[USER_HOME]/.venvs/codex-science/Scripts/python.exe' -B -X utf8 -m cloud_pilot.check_qwen_native
```

Canary source SHA256: `11689751b80d12cde755c52165e4d449ebd4bd324483d1826545b08997670455`.

**Limits:** This verifies the native API, mixed attention/cache path, presence/warper ordering and CPU repeatability for a tiny random model. It does not validate the 27B checkpoint weight mapping, BF16/GPU behavior, Qwen tokenizer prompts, Linux dependency lock, longest-prompt memory, throughput, or scientific translation quality. Full checkpoint/GPU readiness remains partial. The earlier missing-Hub import blocker is resolved only for this explicit subprocess composition.
