provider "kubernetes-alpha" {
  config_path = "../eks/kubeconfig_test-eks-9zgZUcj0"
}
resource "kubernetes_manifest" "app-ns" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "Namespace"
    "metadata" = {
      "name" = "homework"
    }
  }
}
resource "kubernetes_manifest" "app-quota" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "ResourceQuota"
    "metadata" = {
      "name" = "app-resources"
      "namespace" = "homework"
    }
    "spec" = {
      "hard" = {
        "cpu" = "3"
        "memory" = "12Gi"
        "pods" = "8"
      }
    }
  }
}
resource "kubernetes_manifest" "app-sa" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "ServiceAccount"
    "metadata" = {
      "name" = "app"
      "namespace" = "homework"
    }
  }
}
resource "kubernetes_manifest" "app-role" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "rbac.authorization.k8s.io/v1"
    "kind" = "Role"
    "metadata" = {
      "name" = "app"
      "namespace" = "homework"
    }
    "rules" = [
      {
        "apiGroups" = [
          "",
        ]
        "resources" = [
          "configmaps",
          "persistentvolumeclaims",
          "pods",
          "secrets",
          "services",
          "serviceaccounts",
          "volumes",
        ]
        "verbs" = [
          "get",
          "watch",
          "list",
          "create",
          "update",
          "patch",
          "delete",
        ]
      },
      {
        "apiGroups" = [
          "apps",
        ]
        "resources" = [
          "deployments",
        ]
        "verbs" = [
          "get",
          "watch",
          "list",
          "create",
          "update",
          "patch",
          "delete",
        ]
      },
      {
        "apiGroups" = [
          "networking.k8s.io",
        ]
        "resources" = [
          "ingresses",
        ]
        "verbs" = [
          "get",
          "watch",
          "list",
          "create",
          "update",
          "patch",
          "delete",
        ]
      },
    ]
  }
}
resource "kubernetes_manifest" "app-rolebinding" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "rbac.authorization.k8s.io/v1"
    "kind" = "RoleBinding"
    "metadata" = {
      "name" = "app"
      "namespace" = "homework"
    }
    "roleRef" = {
      "apiGroup" = "rbac.authorization.k8s.io"
      "kind" = "Role"
      "name" = "app"
    }
    "subjects" = [
      {
        "kind" = "ServiceAccount"
        "name" = "app"
      },
    ]
  }
}
