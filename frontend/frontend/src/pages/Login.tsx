import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import type { SigninRequest, AuthResponse } from "../types/auth";

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState<SigninRequest>({
    email: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const { data } = await api.post<AuthResponse>("/signin", form);
      localStorage.setItem("token", data.token);
      window.location.href = "/dashboard";
    } catch (error) {
      alert("Login failed");
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>

      <form onSubmit={handleSubmit} className="auth-form">
        <input
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
        />

        <input
          name="password"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
        />

        <button type="submit">Log In</button>
      </form>

      <p>
        Don't have an account?{" "}
        <button
          type="button"
          onClick={() => navigate("/signup")}
          style={{ background: "none", border: "none", color: "blue", cursor: "pointer", textDecoration: "underline" }}
        >
          Sign Up
        </button>
      </p>
    </div>
  );
};

export default Login;
