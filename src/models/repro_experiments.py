import logging
import sys
import pandas as pd
import matplotlib.pyplot as plt
import mlflow
import shap
from dataclasses import asdict

from src.models.model_fit_predict import train_model, evaluate_model, predict_model

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def interpret_features(model, val_features):
    tempdf = pd.DataFrame(val_features, columns=val_features.columns).sample(frac=1)[
        :50
    ]

    # create explainer to compute shap values
    explainer = shap.KernelExplainer(lambda x: model.predict(x), tempdf)

    # compute shap values for all xtest
    shap_values = explainer.shap_values(tempdf)

    plt.subplots(nrows=1, ncols=1)
    shap.summary_plot(shap_values, tempdf, plot_size=(12, 8), show=False)
    plt.savefig(f"artifacts/shap.png")


def log_experiment_mlflow(
    run_name, train_features, train_target, val_features, val_target, train_params
):
    mlflow.set_tracking_uri("http://127.0.0.1:5000/")
    mlflow.set_experiment("demo2")

    with mlflow.start_run(run_name="RUN_{}".format(run_name)) as run:
        logger.info("run_id: {}; status: {}".format(run.info.run_id, run.info.status))

        model = train_model(train_features, train_target, train_params)

        predicted_proba, preds = predict_model(model, val_features)
        metrics = evaluate_model(predicted_proba, preds, val_target)

        mlflow.log_metric(key="f1_val", value=metrics["f1_score"])
        mlflow.log_metric(key="log_loss", value=metrics["log_loss"])
        mlflow.log_metric(key="precision", value=metrics["precision"])
        mlflow.log_metric(key="recall", value=metrics["recall"])

        # convert train_params to dict
        train_params_dict = asdict(train_params)
        mlflow.log_params(train_params_dict)

        interpret_features(model, val_features)

        mlflow.log_artifact(local_path="artifacts/shap.png")
        mlflow.sklearn.log_model(model, "model_saved")
