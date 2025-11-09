import React, { useState } from 'react';
import { useLocation, Link } from 'wouter';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { RootLayout } from '@/components/RootLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

const ForgotPassword: React.FC = () => {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState('');
  const toast = useToast();

  const mutation = useMutation({
    mutationFn: (payload: { email: string }) => apiClient.forgotPassword(payload),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mutation.mutateAsync({ email });
      toast({ title: 'Reset email sent', description: 'If that email exists we sent reset instructions.', status: 'success' });
      setLocation('/signin');
    } catch (err: any) {
      toast({ title: 'Error', description: err?.message || 'Unable to request reset', status: 'error' });
    }
  };

  return (
    <RootLayout>
      <div className="container max-w-lg mx-auto flex-1 flex flex-col justify-center">
        <Card>
          <CardHeader>
            <CardTitle>Forgot password</CardTitle>
            <CardDescription>Enter your email address and we'll send you a link to reset your password.</CardDescription>
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
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <div className="flex items-center justify-between w-full">
                <Button type="submit" disabled={mutation.isLoading}>
                  {mutation.isLoading ? 'Sending...' : 'Send reset link'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => setLocation('/signin')}
                >
                  Back to sign in
                </Button>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </RootLayout>
  );
};

export default ForgotPassword;
