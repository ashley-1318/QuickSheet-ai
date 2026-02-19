import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin } from "@react-oauth/google";
import { setAuthenticationFromGoogle, getIsAuthenticated } from "@/lib/auth";
import { useToast } from "@/hooks/use-toast";

const Login = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    if (getIsAuthenticated()) {
      navigate("/", { replace: true });
    }
  }, [navigate]);

  const handleGoogleSuccess = (credentialResponse: { credential?: string }) => {
    try {
      if (!credentialResponse.credential) {
        throw new Error("No credential received");
      }
      setAuthenticationFromGoogle(credentialResponse.credential);
      navigate("/", { replace: true });
    } catch (error) {
      toast({
        title: "Login failed",
        description: error instanceof Error ? error.message : "Failed to authenticate with Google",
      });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="hero-gradient-bg min-h-screen">
        <div className="container mx-auto flex min-h-screen max-w-5xl items-center justify-center px-6">
          <div className="glass-card w-full max-w-md p-8">
            <div className="mb-8 text-center">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-muted-foreground">
                QuickSheet AI
              </p>
              <h1 className="mt-2 text-3xl font-semibold text-foreground">Sign in to continue</h1>
              <p className="mt-3 text-sm text-muted-foreground">
                Access your study workspace and generate cheat sheets faster.
              </p>
            </div>

            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => {
                  toast({
                    title: "Login failed",
                    description: "Failed to authenticate with Google",
                  });
                }}
                size="large"
              />
            </div>

            <p className="mt-8 text-center text-xs text-muted-foreground">
              By signing in, you agree to the QuickSheet AI terms of service.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
