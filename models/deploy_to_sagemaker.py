import boto3
import tarfile
import os
import joblib
import time
import shutil

# ── Configuration ─────────────────────────────────────────────────────────────
S3_BUCKET      = "financial-assistant-ah"
AWS_REGION     = "us-east-1"
SAGEMAKER_ROLE = "arn:aws:iam::940482435106:role/financial-assistant"
SKLEARN_IMAGE  = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "sagemaker_build")
os.makedirs(BUILD_DIR, exist_ok=True)

s3 = boto3.client("s3", region_name=AWS_REGION)
sm = boto3.client("sagemaker", region_name=AWS_REGION)


def package_model(pkl_filename: str, inference_script: str, tar_filename: str) -> str:
    """
    Bundle model.joblib + code/inference.py (NO setup.py).
    Without setup.py, SageMaker adds /opt/ml/code to sys.path directly
    so 'import inference' works without any pip install step.
    """
    model_path  = os.path.join(BASE_DIR, pkl_filename)
    joblib_path = os.path.join(BUILD_DIR, "model.joblib")
    code_dir    = os.path.join(BUILD_DIR, "code")
    os.makedirs(code_dir, exist_ok=True)

    # Save model
    shutil.copy(model_path, joblib_path)

    # Copy inference script into code/ (no setup.py!)
    
    shutil.copy(
        os.path.join(BASE_DIR, inference_script),
        os.path.join(code_dir, "inference.py")
    )

    tar_path = os.path.join(BUILD_DIR, tar_filename)
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(joblib_path, arcname="model.joblib")
        tar.add(os.path.join(code_dir, "inference.py"), arcname="code/inference.py")

    print(f"✅ Packaged → {tar_filename}")
    return tar_path


def upload_to_s3(local_path: str, s3_key: str) -> str:
    s3.upload_file(local_path, S3_BUCKET, s3_key)
    uri = f"s3://{S3_BUCKET}/{s3_key}"
    print(f"✅ Uploaded → {uri}")
    return uri


def cleanup(model_name: str, endpoint_name: str):
    """Silently delete existing resources before creating new ones."""
    for fn, kwargs in [
        (sm.delete_endpoint,        {"EndpointName": endpoint_name}),
        (sm.delete_endpoint_config, {"EndpointConfigName": f"{endpoint_name}-config"}),
        (sm.delete_model,           {"ModelName": model_name}),
    ]:
        try:
            fn(**kwargs)
            time.sleep(2)
        except Exception:
            pass


def deploy_endpoint(model_uri: str, model_name: str, endpoint_name: str):
    cleanup(model_name, endpoint_name)

    # Create model — no SAGEMAKER_PROGRAM, use default sklearn serving
    sm.create_model(
        ModelName=model_name,
        PrimaryContainer={
            "Image":        SKLEARN_IMAGE,
            "ModelDataUrl": model_uri,
            "Environment": {"SAGEMAKER_PROGRAM": "inference.py","SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/model/code",},
            },
        ExecutionRoleArn=SAGEMAKER_ROLE,
    )
    print(f"✅ Model created: {model_name}")

    # Create endpoint config
    sm.create_endpoint_config(
        EndpointConfigName=f"{endpoint_name}-config",
        ProductionVariants=[{
            "VariantName":          "AllTraffic",
            "ModelName":            model_name,
            "InstanceType":         "ml.m5.large",
            "InitialInstanceCount": 1,
        }],
    )

    # Create endpoint
    sm.create_endpoint(
        EndpointName=endpoint_name,
        EndpointConfigName=f"{endpoint_name}-config",
    )
    print(f"⏳ Deploying {endpoint_name} — waiting up to 20 minutes...")

    waiter = sm.get_waiter("endpoint_in_service")
    waiter.wait(
        EndpointName=endpoint_name,
        WaiterConfig={"Delay": 30, "MaxAttempts": 40},
    )
    print(f"✅ Endpoint live: {endpoint_name}")


if __name__ == "__main__":
    # ── Regression ────────────────────────────────────────────────────────────
    reg_tar = package_model("random_forest_regressor.pkl", "inference_regression.py", "regression_model.tar.gz")
    reg_uri = upload_to_s3(reg_tar, "models/regression_model.tar.gz")
    deploy_endpoint(
        model_uri=reg_uri,
        model_name="housing-regression-model",
        endpoint_name="housing-regression-endpoint",
    )

    # ── Classification ────────────────────────────────────────────────────────
    clf_tar = package_model("logistic_regression_model.pkl", "inference_classification.py", "classification_model.tar.gz")
    clf_uri = upload_to_s3(clf_tar, "models/classification_model.tar.gz")
    deploy_endpoint(
        model_uri=clf_uri,
        model_name="bank-classification-model",
        endpoint_name="bank-classification-endpoint",
    )

    print("\n── Done! Both endpoints are live ──")
    print("REGRESSION_ENDPOINT     = 'housing-regression-endpoint'")
    print("CLASSIFICATION_ENDPOINT = 'bank-classification-endpoint'")