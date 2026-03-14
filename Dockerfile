FROM public.ecr.aws/lambda/python:3.14-arm64

COPY pyproject.toml ${LAMBDA_TASK_ROOT}
COPY uv.lock ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN dnf update -y && \
    dnf install -y openssl && \
    dnf install -y g++ && \
    dnf clean all && \
    python3 -m pip install uv && \
#    uv pip install -r requirements.txt \
#    uv sync --locked \
    python3 -m pip install -r requirements.txt

ADD ./RecordTypes ${LAMBDA_TASK_ROOT}/RecordTypes

# Copy function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]
