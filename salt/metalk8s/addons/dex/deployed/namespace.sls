#!jinja | metalk8s_kubernetes

apiVersion: v1
kind: Namespace
metadata:
  name: metalk8s-auth
  labels:
    app.kubernetes.io/managed-by: salt
    app.kubernetes.io/part-of: metalk8s
    heritage: metalk8s
