import React, { useState } from 'react';
import { useLocation, Link } from 'wouter';
import { useRegister } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { RootLayout } from '@/components/RootLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

const Signup: React.FC = () => {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'learner' | 'mentor'>('learner');

  const registerMutation = useRegister();
  const toast = useToast();

  const next = () => setStep((s) => Math.min(3, s + 1));
  const back = () => setStep((s) => Math.max(1, s - 1));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Basic register payload - expand fields as needed
      await registerMutation.mutateAsync({ email, password, full_name: fullName, role });
      toast({ title: 'Account created', description: 'Welcome!', status: 'success' });
      setLocation('/dashboard');
    } catch (err: any) {
      toast({ title: 'Registration failed', description: err?.message || 'Unknown error', status: 'error' });
    }
  };

  return (
    <RootLayout>
      <div className="container max-w-lg mx-auto flex-1 flex flex-col justify-center">
        <Card>
          <CardHeader>
            <CardTitle>Create an account</CardTitle>
            <CardDescription>Join SkillBridge and start your learning journey</CardDescription>
          </CardHeader>
          
          <form onSubmit={handleSubmit}>
            <CardContent>
              <div className="flex items-center gap-4 mb-6">
                <Button
                  type="button"
                  onClick={() => setStep(1)}
                  variant={step === 1 ? "default" : "outline"}
                  size="sm"
                >
                  1. Account
                </Button>
                <Button
                  type="button"
                  onClick={() => setStep(2)}
                  variant={step === 2 ? "default" : "outline"}
                  size="sm"
                >
                  2. Profile
                </Button>
                <Button
                  type="button"
                  onClick={() => setStep(3)}
                  variant={step === 3 ? "default" : "outline"}
                  size="sm"
                >
                  3. Finish
                </Button>
              </div>

              {step === 1 && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full name</Label>
                    <Input
                      id="fullName"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                      placeholder="Jane Doe"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      placeholder="you@example.com"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      placeholder="Choose a strong password"
                    />
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Select value={role} onValueChange={(value: any) => setRole(value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select your role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="learner">Learner</SelectItem>
                        <SelectItem value="mentor">Mentor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <p className="text-sm text-muted-foreground">You can complete your profile later.</p>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <p>Review your information and submit to create the account.</p>
                  <div className="space-y-2">
                    <div className="flex"><strong>Name:</strong> <span className="ml-2">{fullName}</span></div>
                    <div className="flex"><strong>Email:</strong> <span className="ml-2">{email}</span></div>
                    <div className="flex"><strong>Role:</strong> <span className="ml-2 capitalize">{role}</span></div>
                  </div>
                </div>
              )}
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <div className="flex items-center justify-between w-full">
                <div className="space-x-2">
                  {step > 1 && (
                    <Button type="button" variant="outline" onClick={back}>Back</Button>
                  )}
                  {step < 3 && (
                    <Button type="button" onClick={next}>Next</Button>
                  )}
                </div>

                {step === 3 && (
                  <Button type="submit" disabled={registerMutation.isLoading}>
                    {registerMutation.isLoading ? 'Creating...' : 'Create account'}
                  </Button>
                )}
              </div>

              <div className="text-sm text-muted-foreground">
                Already have an account?{' '}
                <Link href="/signin" className="text-primary hover:underline">
                  Sign in
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </RootLayout>
  );
};

export default Signup;
