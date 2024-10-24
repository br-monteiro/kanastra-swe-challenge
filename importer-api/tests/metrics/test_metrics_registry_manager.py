import pytest
from prometheus_client import REGISTRY
from unittest.mock import MagicMock, patch
from src.metrics.metrics_registry_manager import MetricsRegistryManager, get_metrics


@pytest.fixture(autouse=True)
def before_each():
    MetricsRegistryManager._instance = None


def test_init():
    metrics = MetricsRegistryManager()
    assert metrics.registry == REGISTRY
    assert metrics.metrics_pool == {}
    assert metrics.default_labels == {
        "app": "importer-api"
    }


def test_singleton():
    metrics1 = MetricsRegistryManager()
    metrics2 = MetricsRegistryManager()
    assert metrics1 is metrics2


def test_get():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }
    metrics.get("metric_name", {"key": "value"})
    metrics.metrics_pool["metric_name"].labels.assert_called_with(
        app="importer-api",
        key="value"
    )


def test_get_raises_error():
    metrics = MetricsRegistryManager()
    with pytest.raises(ValueError) as ex:
        metrics.get("metric_name")

    assert str(ex.value) == "Metric metric_name does not exist"


@patch("src.metrics.metrics_registry_manager.Counter")
def test_register_counter(counter, ):
    metrics = MetricsRegistryManager()
    metrics.register_counter("metric_name", "metric_description", {"key"})

    register = metrics.metrics_pool["metric_name"]

    assert register == counter.return_value
    counter.assert_called_with(
        name="metric_name",
        documentation="metric_description",
        registry=metrics.registry,
        labelnames={
            "app",
            "key",
        }
    )


@patch("src.metrics.metrics_registry_manager.Summary")
def test_register_summary(summary, ):
    metrics = MetricsRegistryManager()
    metrics.register_summary("metric_name", "metric_description", {"key"})

    register = metrics.metrics_pool["metric_name"]

    assert register == summary.return_value
    summary.assert_called_with(
        name="metric_name",
        documentation="metric_description",
        registry=metrics.registry,
        labelnames={
            "app",
            "key",
        }
    )


def test_register_counter_raises_error():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }

    with pytest.raises(ValueError) as ex:
        metrics.register_counter("metric_name", "metric_description")

    assert str(ex.value) == "Metric metric_name already exists"


def test_register_summary_raises_error():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }

    with pytest.raises(ValueError) as ex:
        metrics.register_summary("metric_name", "metric_description")

    assert str(ex.value) == "Metric metric_name already exists"


def test_abstract_register():
    metric_constructor = MagicMock()
    metrics = MetricsRegistryManager()
    metrics._abstract_register(
        metric_constructor,
        "metric_name",
        "metric_description",
        {"key"}
    )

    metrics.metrics_pool["metric_name"]

    metric_constructor.assert_called_with(
        name="metric_name",
        documentation="metric_description",
        registry=metrics.registry,
        labelnames={
            "app",
            "key",
        }
    )


def test_abstract_register_raises_error():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }

    with pytest.raises(ValueError) as ex:
        metrics._abstract_register(
            MagicMock,
            "metric_name",
            "metric_description",
            {"key"}
        )

    assert str(ex.value) == "Metric metric_name already exists"


def test_validate_register():
    metrics = MetricsRegistryManager()
    metrics._validate_register("metric_name")


def test_validate_register_raises_error():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }

    with pytest.raises(ValueError) as ex:
        metrics._validate_register("metric_name")

    assert str(ex.value) == "Metric metric_name already exists"


def test_validate_metric():
    metrics = MetricsRegistryManager()
    metrics.metrics_pool = {
        "metric_name": MagicMock()
    }
    metrics._validate_metric("metric_name")


def test_validate_metric_raises_error():
    metrics = MetricsRegistryManager()
    with pytest.raises(ValueError) as ex:
        metrics._validate_metric("metric_name")

    assert str(ex.value) == "Metric metric_name does not exist"


def test_union_labels_values():
    metrics = MetricsRegistryManager()
    labels = metrics._union_labels_values({"key": "value"})

    assert labels == {
        "app": "importer-api",
        "key": "value"
    }


def test_union_labels_keys():
    metrics = MetricsRegistryManager()
    labels = metrics._union_labels_keys({"key"})

    assert labels == {
        "app",
        "key"
    }


@patch("src.metrics.metrics_registry_manager.MetricsRegistryManager")
def test_get_metrics(MetricsRegistryManager):
    metrics = get_metrics()
    MetricsRegistryManager.assert_called_with()
    assert metrics == MetricsRegistryManager.return_value
