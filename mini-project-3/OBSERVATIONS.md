# Kubernetes Mini Project 3 — Observations

## 1. Pod vs Deployment — What's the difference?

A **Pod** is just one running container. Think of it like a single worker.
If that worker gets sick (crashes), nobody replaces them — they're just gone.

A **Deployment** is like a manager who watches over workers.
You tell the manager "I want 3 workers running at all times."
If one crashes, the manager immediately starts a new one.

That's why we never create Pods by hand — we always use Deployments.

---

## 2. Why did we use ConfigMap?

Because we didn't want to hardcode the MongoDB server address inside the app.

Imagine you move your database to a different server tomorrow.
With a ConfigMap, you just update one file and everything still works.
Without it, you'd have to rebuild your entire Docker image — which is slow and annoying.

ConfigMap = "settings file" that lives in Kubernetes, not inside the app code.

---

## 3. What happened when we scaled to 3 replicas?

Kubernetes created 2 more webapp Pods (it already had 1).
Now 3 Pods are all running the same app at the same time.

If one Pod crashes or gets too busy, the other 2 still handle traffic.
Kubernetes automatically splits incoming requests between the 3 Pods.

This is called **load balancing** and it makes the app more reliable.
The coolest part? It happened in seconds just by changing one number.

---

## 4. What happens if MongoDB crashes?

The webapp (mongo-express) will show an error — it can't reach the database.
But the webapp Pods themselves will still be running, just showing error pages.

This is one weakness of our setup — MongoDB has only 1 replica.
In a real production system, you'd use a **StatefulSet** with persistent storage
and run multiple MongoDB replicas so it never has a single point of failure.

For this project, if MongoDB crashes, you can restart it:
```
kubectl rollout restart deployment mongodb-deployment
```

---

## 5. One thing that confused me at first

The most confusing thing was understanding **why Services exist**.

I thought: "The Pods are already running, why do I need a Service?"

The answer is: Pod IP addresses change every time a Pod restarts.
Your app can't keep track of changing IPs by itself.

A **Service** gives a fixed name (like `mongodb-service`) that never changes.
Other apps use that name, and Kubernetes figures out which Pod to send traffic to.

It's basically a stable "phone number" for a group of Pods that might keep changing.
