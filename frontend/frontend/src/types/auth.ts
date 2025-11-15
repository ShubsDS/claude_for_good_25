export interface SignupRequest {
  name: string;
  email: string;
  password: string;
}

export interface SigninRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
}
