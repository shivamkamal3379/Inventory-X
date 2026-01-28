import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, User } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { authService } from '../services/auth';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const result = await authService.login(username, password);
      
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      <form onSubmit={handleLogin} className="space-y-4">
        <div className="space-y-2">
            <div className="relative">
                <User className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                <Input 
                    type="text" 
                    placeholder="Username" 
                    className="pl-10 bg-muted/50 border-border"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
            </div>
        </div>
        <div className="space-y-2">
           <div className="relative">
                <Lock className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                <Input 
                    type="password" 
                    placeholder="Password" 
                    className="pl-10 bg-muted/50 border-border"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
            </div>
        </div>

        {error && (
            <motion.p 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-red-400 text-center"
            >
                {error}
            </motion.p>
        )}

        <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-primary to-purple-600 hover:from-primary/90 hover:to-purple-600/90"
            isLoading={isLoading}
        >
            Sign In
        </Button>
      </form>
      
      <div className="text-center text-xs text-muted-foreground">
        Use <strong>admin</strong> / <strong>password</strong> to login
      </div>

      <div className="text-center pt-4">
        <Button variant="link" onClick={() => navigate('/')} className="text-muted-foreground hover:text-primary">
            ← Return to Home
        </Button>
      </div>
    </motion.div>
  );
}
