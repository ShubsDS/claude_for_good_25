import React, { useEffect, useState } from "react";
import api from "../api/axios";

const Dashboard: React.FC = () => {
  const [email, setEmail] = useState<string>("");

  useEffect(() => {
    async function fetchMe() {
      try {
        const token = localStorage.getItem("token");
        const { data } = await api.get("/authtest", {
          params: { token },
        });

        setEmail(data.email);
      } catch {
        window.location.href = "/login";
      }
    }

    fetchMe();
  }, []);

  return (
    <div>
      <h1>Welcome!</h1>
      <p>You are logged in as: {email}</p>

      <button
        onClick={() => {
          localStorage.removeItem("token");
          window.location.href = "/login";
        }}
      >
        Log Out
      </button>
    </div>
  );
};

export default Dashboard;
