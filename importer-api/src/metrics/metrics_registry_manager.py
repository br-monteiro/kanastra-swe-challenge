from prometheus_client import REGISTRY, Counter, Summary


class MetricsRegistryManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MetricsRegistryManager, cls).__new__(cls)
            cls._instance.registry = REGISTRY
            cls._instance.metrics_pool = {}
            cls._instance.default_labels = {
                "app": "importer-api"
            }
        return cls._instance

    def get(self, metric_name: str, labels: dict[str, str] = {}):
        self._validate_metric(metric_name)

        _labels = self._union_labels_values(labels)

        return self.metrics_pool[metric_name].labels(**_labels)

    def register_counter(self, metric_name: str, metric_description: str, labels: set[str] = {}):
        self._abstract_register(
            Counter,
            metric_name,
            metric_description,
            labels
        )

    def register_summary(self, metric_name: str, metric_description: str, labels: set[str] = {}):
        self._abstract_register(
            Summary,
            metric_name,
            metric_description,
            labels
        )

    def _abstract_register(self, metric_constructor, metric_name: str, metric_description: str, labels: set[str] = {}):
        self._validate_register(metric_name)

        self.metrics_pool[metric_name] = metric_constructor(
            name=metric_name,
            documentation=metric_description,
            registry=self.registry,
            labelnames=self._union_labels_keys(labels)
        )

    def _validate_register(self, metric_name: str):
        if metric_name in self.metrics_pool:
            raise ValueError(f"Metric {metric_name} already exists")

    def _validate_metric(self, metric_name: str):
        if metric_name not in self.metrics_pool:
            raise ValueError(f"Metric {metric_name} does not exist")

    def _union_labels_values(self, labels: dict[str, str]):
        _labels = self.default_labels.copy()
        _labels.update(labels)

        return _labels

    def _union_labels_keys(self, labels: set[str]):
        label_keys = set(self.default_labels.keys())
        return label_keys.union(labels)


def get_metrics():
    return MetricsRegistryManager()
