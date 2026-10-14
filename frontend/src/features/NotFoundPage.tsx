import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Home, ArrowLeft } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4">
      <Card className="max-w-md w-full text-center py-10">
        <span className="text-5xl block mb-4">🌾</span>
        <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-2">404</h1>
        <h2 className="text-base font-bold text-slate-700 dark:text-slate-300 mb-2">
          Page Not Found / પેજ મળ્યું નથી
        </h2>
        <p className="text-xs text-slate-500 mb-6 max-w-xs mx-auto">
          The requested farm or advisory page does not exist or has been relocated.
        </p>

        <div className="flex justify-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(-1)}
            leftIcon={<ArrowLeft className="w-4 h-4" />}
          >
            Go Back
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => navigate('/dashboard')}
            leftIcon={<Home className="w-4 h-4" />}
          >
            Farm Home
          </Button>
        </div>
      </Card>
    </div>
  );
};
