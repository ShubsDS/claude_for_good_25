import React, { useState } from "react";
import api from "../api/axios";
import type { SignupRequest, AuthResponse } from "../types/auth";

const Signup: React.FC = () => {
  const [form, setForm] = useState<SignupRequest>({
    name: "",
    email: "",
    password: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const { data } = await api.post<AuthResponse>("/signup", form);
      localStorage.setItem("token", data.token);
      window.location.href = "/dashboard";
    } catch (error) {
      alert("Signup failed");
    }
  };

  return (
    <div className="auth-container">
      <h2>Create Account</h2>

      <form onSubmit={handleSubmit} className="auth-form">
        <input
          name="name"
          placeholder="Full Name"
          value={form.name}
          onChange={handleChange}
        />

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

        <button type="submit">Sign Up</button>
      </form>
    </div>
  );
};

export default Signup;
