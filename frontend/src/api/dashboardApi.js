import client from "./client";

export function getDashboard() {
  return client.get("/api/dashboard");
}
