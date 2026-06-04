# Kubernetes Mini Project 3 — Complete Guide

Two-tier app on Minikube: **MongoDB (database) + mongo-express (web UI)**

---

## PROJECT STRUCTURE

```
mini-project-3/
├── k8s/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── mongodb-deployment.yaml
│   ├── mongodb-service.yaml
│   ├── webapp-deployment.yaml
│   └── webapp-service.yaml
├── OBSERVATIONS.md
└── README.md
```

---

## STEP 1 — SETUP (Install tools)

### Check if Docker is running
Open PowerShell and run:
```powershell
docker --version
```
If you see a version number, Docker is installed. If not, download it from:
👉 https://www.docker.com/products/docker-desktop/
Install it, start it, and wait until it says "Docker is running".

---

### Install Minikube (Windows)
Run this in PowerShell **as Administrator**:
```powershell
winget install Kubernetes.minikube
```
Or download the `.exe` directly:
👉 https://minikube.sigs.k8s.io/docs/start/

After install, verify:
```powershell
minikube version
```

---

### Install kubectl (Windows)
Run this in PowerShell **as Administrator**:
```powershell
winget install Kubernetes.kubectl
```

After install, verify:
```powershell
kubectl version --client
```

---

## STEP 2 — START THE CLUSTER

Start Minikube with Docker as the driver:
```powershell
minikube start --driver=docker
```

Wait until you see: `Done! kubectl is now configured to use "minikube"`

Verify the cluster is running:
```powershell
minikube status
```
Expected output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

Also run:
```powershell
kubectl get nodes
```
Expected output:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.xx.x
```

> 📸 **SCREENSHOT 1** — Take a screenshot now. Show the terminal with `minikube status` output and `kubectl get nodes` showing STATUS: Ready.

---

## STEP 3 — WHAT'S IN EACH FILE

### Credentials (Secret)
- Username: `admin`
- Password: `password123`
- These are stored base64 encoded in `secret.yaml`
  - `admin` → `YWRtaW4=`
  - `password123` → `cGFzc3dvcmQxMjM=`

### ConfigMap
- Tells the webapp which server MongoDB is on: `mongodb-service`
- Tells it which port: `27017`

### Deployments
- **mongodb-deployment**: runs 1 MongoDB Pod, reads credentials from Secret
- **webapp-deployment**: runs mongo-express UI, reads config from ConfigMap + Secret

### Services
- **mongodb-service**: internal only (ClusterIP), lets webapp reach MongoDB
- **webapp-service**: external (NodePort 30100), lets your browser reach the webapp

---

## STEP 4 — YAML FILES (Full Content)

### === configmap.yaml ===
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: webapp-config
data:
  ME_CONFIG_MONGODB_SERVER: "mongodb-service"
  ME_CONFIG_MONGODB_PORT: "27017"
```

### === secret.yaml ===
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mongodb-secret
type: Opaque
data:
  mongo-root-username: YWRtaW4=
  mongo-root-password: cGFzc3dvcmQxMjM=
```

### === mongodb-deployment.yaml ===
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb-deployment
  labels:
    app: mongodb
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
        - name: mongodb
          image: mongo:6.0
          ports:
            - containerPort: 27017
          env:
            - name: MONGO_INITDB_ROOT_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: MONGO_INITDB_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
```

### === mongodb-service.yaml ===
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
spec:
  selector:
    app: mongodb
  ports:
    - protocol: TCP
      port: 27017
      targetPort: 27017
```

### === webapp-deployment.yaml ===
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webapp-deployment
  labels:
    app: webapp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: webapp
  template:
    metadata:
      labels:
        app: webapp
    spec:
      containers:
        - name: mongo-express
          image: mongo-express:1.0.0-alpha.4
          ports:
            - containerPort: 8081
          env:
            - name: ME_CONFIG_MONGODB_ADMINUSERNAME
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-username
            - name: ME_CONFIG_MONGODB_ADMINPASSWORD
              valueFrom:
                secretKeyRef:
                  name: mongodb-secret
                  key: mongo-root-password
            - name: ME_CONFIG_MONGODB_SERVER
              valueFrom:
                configMapKeyRef:
                  name: webapp-config
                  key: ME_CONFIG_MONGODB_SERVER
            - name: ME_CONFIG_MONGODB_PORT
              valueFrom:
                configMapKeyRef:
                  name: webapp-config
                  key: ME_CONFIG_MONGODB_PORT
```

### === webapp-service.yaml ===
```yaml
apiVersion: v1
kind: Service
metadata:
  name: webapp-service
spec:
  selector:
    app: webapp
  type: NodePort
  ports:
    - protocol: TCP
      port: 8081
      targetPort: 8081
      nodePort: 30100
```

---

## STEP 5 — DEPLOY EVERYTHING (In This Exact Order)

Go to your project folder first:
```powershell
cd C:\Users\Gaye\Desktop\fastapi-journey\mini-project-3
```

Now apply files **in this order** (order matters!):
```powershell
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/mongodb-deployment.yaml
kubectl apply -f k8s/mongodb-service.yaml
kubectl apply -f k8s/webapp-deployment.yaml
kubectl apply -f k8s/webapp-service.yaml
```

Wait about 30–60 seconds for Pods to start pulling images and become ready.

---

## STEP 6 — VERIFY EVERYTHING IS RUNNING

```powershell
kubectl get all
```

Expected output (yours may look similar):
```
NAME                                      READY   STATUS    RESTARTS   AGE
pod/mongodb-deployment-xxxxxxx-xxxxx      1/1     Running   0          1m
pod/webapp-deployment-xxxxxxx-xxxxx       1/1     Running   0          1m

NAME                      TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)
service/kubernetes        ClusterIP   10.96.0.1        <none>        443/TCP
service/mongodb-service   ClusterIP   10.101.xxx.xxx   <none>        27017/TCP
service/webapp-service    NodePort    10.106.xxx.xxx   <none>        8081:30100/TCP

NAME                                 READY   UP-TO-DATE   AVAILABLE
deployment.apps/mongodb-deployment   1/1     1            1
deployment.apps/webapp-deployment    1/1     1            1
```

All Pods must show `STATUS: Running` and `READY: 1/1` before continuing.

If a Pod is stuck in `Pending` or `ContainerCreating`, wait a bit more, then check:
```powershell
kubectl describe pod <pod-name>
```

> 📸 **SCREENSHOT 2** — Take a screenshot of `kubectl get all` showing all Pods Running and all Services listed.

---

## STEP 7 — OPEN THE APP IN YOUR BROWSER

```powershell
minikube service webapp-service
```

This will **automatically open** your browser at something like:
`http://127.0.0.1:30100`

What you will see:
- The **mongo-express** web interface
- A list of MongoDB databases (admin, config, local)
- You can click "Create Database" and add a new one
- The app is connected to your MongoDB Pod!

> 📸 **SCREENSHOT 3** — Take a screenshot of the browser showing the mongo-express UI. The URL should be visible (http://127.0.0.1:xxxxx or similar).

---

## STEP 8 — SCALE THE WEBAPP TO 3 REPLICAS

Open the file `k8s/webapp-deployment.yaml` and change **one line**:

Find this:
```yaml
  replicas: 1
```

Change it to:
```yaml
  replicas: 3
```

Save the file. Then run:
```powershell
kubectl apply -f k8s/webapp-deployment.yaml
```

Now check the Pods:
```powershell
kubectl get pods
```

Expected result — you should see **3 webapp Pods** running:
```
NAME                                    READY   STATUS    RESTARTS   AGE
mongodb-deployment-xxxxxxx-xxxxx        1/1     Running   0          5m
webapp-deployment-xxxxxxx-aaaaa         1/1     Running   0          5m
webapp-deployment-xxxxxxx-bbbbb         1/1     Running   0          30s
webapp-deployment-xxxxxxx-ccccc         1/1     Running   0          30s
```

> 📸 **SCREENSHOT 4** — Take a screenshot of `kubectl get pods` showing 3 webapp Pods all with STATUS: Running.

---

## STEP 9 — SCREENSHOT CHECKLIST

| # | When to Take It | What Must Be Visible |
|---|-----------------|----------------------|
| 1 | After `minikube status` | Terminal showing host/kubelet/apiserver all "Running" + kubectl get nodes STATUS=Ready |
| 2 | After `kubectl get all` | All 4 resources (2 Pods, 2 Deployments, Services) with Running status |
| 3 | After browser opens | mongo-express UI in browser, database list visible |
| 4 | After scaling to 3 | `kubectl get pods` showing 3 webapp Pods all Running |

---

## STEP 10 — GITHUB COMMANDS

### First time: Initialize git in your project
```powershell
cd C:\Users\Gaye\Desktop\fastapi-journey
git init
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
```
(Replace with your actual GitHub repo URL)

### Create a new branch for this project
```powershell
git checkout -b mini-project-3
```

### Commit Step 1 — Add YAML config files
```powershell
git add mini-project-3/k8s/configmap.yaml mini-project-3/k8s/secret.yaml
git commit -m "mini-project-3: add ConfigMap and Secret"
```

### Commit Step 2 — Add MongoDB files
```powershell
git add mini-project-3/k8s/mongodb-deployment.yaml mini-project-3/k8s/mongodb-service.yaml
git commit -m "mini-project-3: add MongoDB Deployment and Service"
```

### Commit Step 3 — Add WebApp files
```powershell
git add mini-project-3/k8s/webapp-deployment.yaml mini-project-3/k8s/webapp-service.yaml
git commit -m "mini-project-3: add WebApp Deployment and Service"
```

### Commit Step 4 — Add documentation
```powershell
git add mini-project-3/OBSERVATIONS.md mini-project-3/README.md
git commit -m "mini-project-3: add README and OBSERVATIONS"
```

### Push to GitHub
```powershell
git push -u origin mini-project-3
```

---

## CLEANUP (Optional — when you're done)

Stop Minikube to free resources:
```powershell
minikube stop
```

To delete the cluster completely:
```powershell
minikube delete
```

---

## QUICK REFERENCE — Useful Commands

| Command | What it does |
|---------|-------------|
| `kubectl get all` | See everything running |
| `kubectl get pods` | See only Pods |
| `kubectl get services` | See only Services |
| `kubectl describe pod <name>` | See details + errors for a Pod |
| `kubectl logs <pod-name>` | See logs from a Pod |
| `kubectl delete -f k8s/` | Delete everything |
| `minikube dashboard` | Open Kubernetes dashboard in browser |
