# Build and exercise this on a free/preparation Linux host BEFORE GPU rental.
FROM pytorch/pytorch@sha256:eee11b3b3872a8c838e35ef48f08b2d5def2080902c7f666831310ca1a0ef2be
WORKDIR /opt/pahlavi
COPY requirements-linux.lock .
RUN python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version" \
 && python -m pip uninstall --break-system-packages --yes spin \
 && python -m pip install --break-system-packages --no-cache-dir --only-binary=:all: --require-hashes --extra-index-url https://download.pytorch.org/whl/cu128 -r requirements-linux.lock \
 && python -m pip check
COPY runtime.py bundle.py fetch_base.py ./
ENV HF_HUB_DISABLE_TELEMETRY=1 PYTHONDONTWRITEBYTECODE=1
RUN python runtime.py tiny-smoke --device cpu --four-bit
ENTRYPOINT ["python", "/opt/pahlavi/runtime.py"]
