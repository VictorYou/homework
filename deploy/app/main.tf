provider "kubernetes-alpha" {
  config_path = "../eks/kubeconfig_test-eks-zljvsHOJ"
}
resource "kubernetes_manifest" "tvnf-quota" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "ResourceQuota"
    "metadata" = {
      "name" = "tvnf-resources"
      "namespace" = "fastpass-tvnf"
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
resource "kubernetes_manifest" "tvnf-ns" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "Namespace"
    "metadata" = {
      "name" = "fastpass-tvnf"
    }
  }
}
resource "kubernetes_manifest" "tvnf-sa" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "v1"
    "kind" = "ServiceAccount"
    "metadata" = {
      "name" = "tvnf"
      "namespace" = "fastpass-tvnf"
    }
  }
}
resource "kubernetes_manifest" "tvnf-role" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "rbac.authorization.k8s.io/v1"
    "kind" = "Role"
    "metadata" = {
      "name" = "tvnf"
      "namespace" = "fastpass-tvnf"
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
resource "kubernetes_manifest" "tvnf-rolebinding" {
  provider = kubernetes-alpha
  manifest = {
    "apiVersion" = "rbac.authorization.k8s.io/v1"
    "kind" = "RoleBinding"
    "metadata" = {
      "name" = "tvnf"
      "namespace" = "fastpass-tvnf"
    }
    "roleRef" = {
      "apiGroup" = "rbac.authorization.k8s.io"
      "kind" = "Role"
      "name" = "tvnf"
    }
    "subjects" = [
      {
        "kind" = "ServiceAccount"
        "name" = "tvnf"
      },
    ]
  }
}
