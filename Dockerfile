FROM amazon/aws-lambda-python:3.14-arm64

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN dnf update -y && \
    dnf install -y openssl && \
    dnf install -y g++ && \
    dnf clean all && \
    python3 -m pip install -r requirements.txt
#    python3 -m pip install -r /requirements.txt - target ${LAMBDA_TASK_ROOT}

# Copy function code
COPY main.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]
