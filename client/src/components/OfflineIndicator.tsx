import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [showIndicator, setShowIndicator] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setShowIndicator(true);
      toast({
        title: "Back Online",
        description: "You're connected to the internet again.",
      });
      // Hide indicator after 3 seconds
      setTimeout(() => setShowIndicator(false), 3000);
    };

    const handleOffline = () => {
      setIsOnline(false);
      setShowIndicator(true);
      toast({
        title: "You're Offline",
        description: "Some features may not work. Your data will sync when you're back online.",
        variant: "destructive",
      });
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [toast]);

  if (!showIndicator) return null;

  return (
    <div className="fixed top-4 right-4 z-50">
      <Card className={`transition-all duration-300 ${
        isOnline ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
      }`}>
        <CardContent className="p-3">
          <div className="flex items-center gap-2">
            {isOnline ? (
              <Wifi className="h-4 w-4 text-green-600" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-600" />
            )}
            <Badge variant={isOnline ? "default" : "destructive"} className="text-xs">
              {isOnline ? "Online" : "Offline"}
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Hook for checking online status
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
};

// Hook for offline queue management
export const useOfflineQueue = () => {
  const [queue, setQueue] = useState<any[]>([]);

  const addToQueue = (item: any) => {
    setQueue(prev => [...prev, { ...item, id: Date.now(), timestamp: new Date() }]);
  };

  const removeFromQueue = (id: number) => {
    setQueue(prev => prev.filter(item => item.id !== id));
  };

  const clearQueue = () => {
    setQueue([]);
  };

  return {
    queue,
    addToQueue,
    removeFromQueue,
    clearQueue,
    hasItems: queue.length > 0
  };
};