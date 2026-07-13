#!/usr/bin/env bash

set -euo pipefail

export LC_NUMERIC=C  # Force dot as decimal separator regardless of system locale

OUTPUT_FILE="${1:-.docker.gpu.env}"
REQUESTED_STACK="${GPU_STACK_PROFILE:-auto}"

if [[ "${REQUESTED_STACK}" != "auto" && "${REQUESTED_STACK}" != "legacy" && "${REQUESTED_STACK}" != "nextgen" && "${REQUESTED_STACK}" != "grace" ]]; then
  echo "Invalid GPU_STACK_PROFILE='${REQUESTED_STACK}'. Use auto, legacy, nextgen, or grace." >&2
  exit 1
fi

LEGACY_BUILDER_IMAGE="nvidia/cuda:12.6.0-cudnn-devel-ubuntu24.04"
LEGACY_TORCH_INDEX_URL="https://download.pytorch.org/whl/cu126"
LEGACY_TORCH_CUDA_ARCH_LIST="6.1;7.0;7.5;8.0;8.6;8.9;9.0+PTX"

NEXTGEN_BUILDER_IMAGE="nvidia/cuda:12.8.0-cudnn-devel-ubuntu24.04"
NEXTGEN_TORCH_INDEX_URL="https://download.pytorch.org/whl/cu128"
NEXTGEN_TORCH_CUDA_ARCH_LIST="8.0;8.6;8.9;9.0;12.0+PTX"

# NVIDIA Grace-Blackwell (aarch64), e.g. DGX Spark (GB10, sm_121). Not
# auto-detected: nextgen's compute-capability check (>= 10.0) already matches
# these GPUs and works via PTX JIT, so this profile is an explicit opt-in for
# native CUDA 13 / SASS on aarch64 hosts instead. See the README's "ARM64 /
# NVIDIA Grace-Blackwell" section for verified hardware notes.
GRACE_BUILDER_IMAGE="nvidia/cuda:13.0.3-cudnn-devel-ubuntu24.04"
GRACE_TORCH_INDEX_URL="https://download.pytorch.org/whl/cu130"
GRACE_TORCH_CUDA_ARCH_LIST="12.0;12.1"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found; cannot detect GPU profile" >&2
  exit 1
fi

GPU_NAME="$(nvidia-smi --query-gpu=name --format=csv,noheader | sed -n '1p')"
GPU_COMPUTE_CAPABILITY="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | sed -n '1p' | tr -d ' ')"

BUILDER_IMAGE="${LEGACY_BUILDER_IMAGE}"
TORCH_INDEX_URL="${LEGACY_TORCH_INDEX_URL}"
TORCH_CUDA_ARCH_LIST="${LEGACY_TORCH_CUDA_ARCH_LIST}"
GPU_STACK="legacy"

if [[ -n "${GPU_COMPUTE_CAPABILITY}" ]] && awk "BEGIN {exit !(${GPU_COMPUTE_CAPABILITY} >= 10.0)}"; then
  BUILDER_IMAGE="${NEXTGEN_BUILDER_IMAGE}"
  TORCH_INDEX_URL="${NEXTGEN_TORCH_INDEX_URL}"
  TORCH_CUDA_ARCH_LIST="${NEXTGEN_TORCH_CUDA_ARCH_LIST}"
  GPU_STACK="nextgen"
fi

if [[ "${REQUESTED_STACK}" == "legacy" ]]; then
  BUILDER_IMAGE="${LEGACY_BUILDER_IMAGE}"
  TORCH_INDEX_URL="${LEGACY_TORCH_INDEX_URL}"
  TORCH_CUDA_ARCH_LIST="${LEGACY_TORCH_CUDA_ARCH_LIST}"
  GPU_STACK="legacy"
fi

if [[ "${REQUESTED_STACK}" == "nextgen" ]]; then
  BUILDER_IMAGE="${NEXTGEN_BUILDER_IMAGE}"
  TORCH_INDEX_URL="${NEXTGEN_TORCH_INDEX_URL}"
  TORCH_CUDA_ARCH_LIST="${NEXTGEN_TORCH_CUDA_ARCH_LIST}"
  GPU_STACK="nextgen"
fi

if [[ "${REQUESTED_STACK}" == "grace" ]]; then
  BUILDER_IMAGE="${GRACE_BUILDER_IMAGE}"
  TORCH_INDEX_URL="${GRACE_TORCH_INDEX_URL}"
  TORCH_CUDA_ARCH_LIST="${GRACE_TORCH_CUDA_ARCH_LIST}"
  GPU_STACK="grace"
fi

cat >"${OUTPUT_FILE}" <<EOF
BUILDER_IMAGE=${BUILDER_IMAGE}
TORCH_INDEX_URL=${TORCH_INDEX_URL}
TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}
GPU_STACK=${GPU_STACK}
EOF

echo "Detected GPU: ${GPU_NAME}"
if [[ -n "${GPU_COMPUTE_CAPABILITY}" ]]; then
  echo "Detected compute capability: ${GPU_COMPUTE_CAPABILITY}"
else
  echo "Detected compute capability: unavailable (kept legacy unless overridden)"
fi
echo "Selected GPU stack: ${GPU_STACK}"
echo "Wrote Docker build args to ${OUTPUT_FILE}"
