FROM public.ecr.aws/lambda/python:3.14 AS build

COPY --from=ghcr.io/astral-sh/uv:0.9.22 /uv /usr/local/bin/uv

WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project --output-file requirements.txt \
    && uv pip install --python /var/lang/bin/python3.14 \
        --no-cache --require-hashes --target /packages -r requirements.txt

FROM public.ecr.aws/lambda/python:3.14

COPY --from=build /packages/ ${LAMBDA_TASK_ROOT}/
COPY src/ ${LAMBDA_TASK_ROOT}/src/

CMD ["src.functions.handler.handler"]
