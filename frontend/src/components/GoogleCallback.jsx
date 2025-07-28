import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import axios from 'axios';

const GoogleCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { handleGoogleCallback } = useAuthStore();

  useEffect(() => {
    const code = searchParams.get('code');
    if (code) {
      // Call the backend to handle the Google callback
      axios.get(`/api/auth/google/callback?code=${code}`)
        .then((response) => {
          const { user, token } = response.data;
          handleGoogleCallback(user, token).then((result) => {
            if (result.success) {
              navigate('/dashboard');
            } else {
              navigate('/login?error=google_auth_failed');
            }
          });
        })
        .catch((error) => {
          console.error('Google callback error:', error);
          navigate('/login?error=google_auth_failed');
        });
    } else {
      navigate('/login');
    }
  }, [searchParams, handleGoogleCallback, navigate]);

  return (
    <div className="d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
      <div className="text-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3">Completing Google authentication...</p>
      </div>
    </div>
  );
};

export default GoogleCallback; 