def generate_dockerfile(required_python_version, additional_packages):
    dockerfile_content = f"""
    FROM python:{required_python_version}
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir {' '.join(additional_packages)}
    CMD ["python", "your_script.py"]
    """

    with open('Dockerfile', 'w') as dockerfile:
        dockerfile.write(dockerfile_content)

generate_dockerfile('3.8', ['numpy', 'pandas'])