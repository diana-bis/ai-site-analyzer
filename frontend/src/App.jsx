import { useEffect, useState } from "react";
import client from "./api/client";

// Temporary Step 0 probe: proves frontend <-> backend connectivity before
// any real pages exist. Replaced by routing in Step 5.
function App() {
  const [status, setStatus] = useState("checking...");

  useEffect(() => {
    client
      .get("/api/health")
      .then((response) => setStatus(JSON.stringify(response.data)))
      .catch((error) => setStatus(`error: ${error.message}`));
  }, []);

  return (
    <div>
      <h1>AI Site Analyzer</h1>
      <p>Backend health check: {status}</p>
    </div>
  );
}

export default App;
