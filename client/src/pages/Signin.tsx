import React, { useState } from 'react';
import { useLocation } from 'wouter';
import { useLogin } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { RootLayout } from '@/components/RootLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Link } from 'wouter';

const Signin: React.FC = () => {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const loginMutation = useLogin();
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await loginMutation.mutateAsync({ email, password });
      toast({ title: 'Signed in', description: 'Welcome back!', status: 'success' });
      setLocation('/dashboard');
    } catch (err: any) {
      toast({ title: 'Sign in failed', description: err?.message || 'Unknown error', status: 'error' });
    }
  };

  return (
    <RootLayout>
      <div className="container max-w-lg mx-auto flex-1 flex flex-col justify-center">
        <Card>
          <CardHeader>
            <CardTitle>Sign in</CardTitle>
            <CardDescription>Enter your credentials to access your account</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  type="email"
                  required
                  placeholder="you@example.com"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  type="password"
                  required
                  placeholder="••••••••"
                />
              </div>
            </CardContent>
            
            <CardFooter className="flex flex-col space-y-4">
              <div className="flex items-center justify-between w-full">
                <Button type="submit" disabled={loginMutation.isLoading}>
                  {loginMutation.isLoading ? 'Signing in...' : 'Sign in'}
                </Button>
                <Link href="/forgot-password" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>

              <div className="text-sm text-muted-foreground">
                Don't have an account?{' '}
                <Link href="/signup" className="text-primary hover:underline">
                  Sign up
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </RootLayout>
  );
};

export default Signin;
