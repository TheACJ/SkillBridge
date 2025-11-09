import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DashboardLayout } from "@/components/DashboardLayout";
import { apiClient } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "@/lib/theme-provider";
import {
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  Key,
  Upload,
  Save,
  Eye,
  EyeOff
} from "lucide-react";

export default function Settings() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Form states
  const [profileData, setProfileData] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    bio: "",
    location: "",
    github_username: "",
    linkedin_url: "",
    portfolio_url: "",
    timezone: "UTC",
    languages: ["en"]
  });

  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });

  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: true,
    push_notifications: true,
    mentorship_requests: true,
    roadmap_updates: true,
    badge_earned: true,
    weekly_digest: true,
    marketing_emails: false
  });

  const [privacySettings, setPrivacySettings] = useState({
    profile_visibility: "public",
    show_progress: true,
    show_badges: true,
    allow_mentoring: true,
    data_sharing: false
  });

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  // Mutations
  const updateProfileMutation = useMutation({
    mutationFn: (data: typeof profileData) => apiClient.updateUserProfile(data),
    onSuccess: () => {
      toast({
        title: "Profile Updated",
        description: "Your profile has been updated successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update profile",
        variant: "destructive",
      });
    },
  });

  const changePasswordMutation = useMutation({
    mutationFn: (data: typeof passwordData) => apiClient.changePassword(data),
    onSuccess: () => {
      toast({
        title: "Password Changed",
        description: "Your password has been changed successfully.",
      });
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: ""
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to change password",
        variant: "destructive",
      });
    },
  });

  const updateNotificationSettingsMutation = useMutation({
    mutationFn: (settings: typeof notificationSettings) => apiClient.updateNotificationSettings(settings),
    onSuccess: () => {
      toast({
        title: "Settings Updated",
        description: "Notification preferences have been saved.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update notification settings",
        variant: "destructive",
      });
    },
  });

  const updatePrivacySettingsMutation = useMutation({
    mutationFn: (settings: typeof privacySettings) => apiClient.updatePrivacySettings(settings),
    onSuccess: () => {
      toast({
        title: "Privacy Settings Updated",
        description: "Your privacy preferences have been saved.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update privacy settings",
        variant: "destructive",
      });
    },
  });

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateProfileMutation.mutate(profileData);
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast({
        title: "Error",
        description: "New passwords do not match",
        variant: "destructive",
      });
      return;
    }
    changePasswordMutation.mutate(passwordData);
  };

  const handleNotificationSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateNotificationSettingsMutation.mutate(notificationSettings);
  };

  const handlePrivacySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updatePrivacySettingsMutation.mutate(privacySettings);
  };

  const timezones = [
    "UTC", "America/New_York", "America/Los_Angeles", "Europe/London",
    "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", "Australia/Sydney"
  ];

  const languages = [
    { code: "en", name: "English" },
    { code: "es", name: "Spanish" },
    { code: "fr", name: "French" },
    { code: "de", name: "German" },
    { code: "zh", name: "Chinese" },
    { code: "ja", name: "Japanese" }
  ];

  return (
    <DashboardLayout activeSection="settings">
      <div className="p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold mb-2">Settings</h1>
            <p className="text-muted-foreground">
              Manage your account preferences and privacy settings
            </p>
          </div>

          <Tabs defaultValue="profile" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
              <TabsTrigger value="notifications">Notifications</TabsTrigger>
              <TabsTrigger value="privacy">Privacy</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
            </TabsList>

            {/* Profile Settings */}
            <TabsContent value="profile" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Profile Information
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleProfileSubmit} className="space-y-6">
                    {/* Avatar Section */}
                    <div className="flex items-center gap-6">
                      <Avatar className="h-20 w-20">
                        <AvatarImage src={undefined} alt={user?.first_name} />
                        <AvatarFallback className="text-lg">
                          {user?.first_name?.[0]}{user?.last_name?.[0]}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <Button variant="outline" size="sm">
                          <Upload className="h-4 w-4 mr-2" />
                          Change Avatar
                        </Button>
                        <p className="text-sm text-muted-foreground mt-2">
                          JPG, PNG or GIF. Max size 2MB.
                        </p>
                      </div>
                    </div>

                    {/* Basic Info */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="first_name">First Name</Label>
                        <Input
                          id="first_name"
                          value={profileData.first_name}
                          onChange={(e) => setProfileData(prev => ({ ...prev, first_name: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="last_name">Last Name</Label>
                        <Input
                          id="last_name"
                          value={profileData.last_name}
                          onChange={(e) => setProfileData(prev => ({ ...prev, last_name: e.target.value }))}
                        />
                      </div>
                    </div>

                    {/* Bio */}
                    <div className="space-y-2">
                      <Label htmlFor="bio">Bio</Label>
                      <textarea
                        id="bio"
                        className="w-full p-3 border rounded-md resize-none"
                        rows={3}
                        placeholder="Tell others about yourself..."
                        value={profileData.bio}
                        onChange={(e) => setProfileData(prev => ({ ...prev, bio: e.target.value }))}
                      />
                    </div>

                    {/* Location and Links */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="location">Location</Label>
                        <Input
                          id="location"
                          placeholder="City, Country"
                          value={profileData.location}
                          onChange={(e) => setProfileData(prev => ({ ...prev, location: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="timezone">Timezone</Label>
                        <Select value={profileData.timezone} onValueChange={(value) => setProfileData(prev => ({ ...prev, timezone: value }))}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {timezones.map((tz) => (
                              <SelectItem key={tz} value={tz}>{tz}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Social Links */}
                    <div className="space-y-4">
                      <h4 className="font-medium">Social Links</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="github">GitHub Username</Label>
                          <Input
                            id="github"
                            placeholder="username"
                            value={profileData.github_username}
                            onChange={(e) => setProfileData(prev => ({ ...prev, github_username: e.target.value }))}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="linkedin">LinkedIn URL</Label>
                          <Input
                            id="linkedin"
                            placeholder="https://linkedin.com/in/username"
                            value={profileData.linkedin_url}
                            onChange={(e) => setProfileData(prev => ({ ...prev, linkedin_url: e.target.value }))}
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="portfolio">Portfolio URL</Label>
                        <Input
                          id="portfolio"
                          placeholder="https://yourportfolio.com"
                          value={profileData.portfolio_url}
                          onChange={(e) => setProfileData(prev => ({ ...prev, portfolio_url: e.target.value }))}
                        />
                      </div>
                    </div>

                    <Button type="submit" disabled={updateProfileMutation.isPending}>
                      <Save className="h-4 w-4 mr-2" />
                      {updateProfileMutation.isPending ? "Saving..." : "Save Changes"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Security Settings */}
            <TabsContent value="security" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Key className="h-5 w-5" />
                    Change Password
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePasswordSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="current_password">Current Password</Label>
                      <div className="relative">
                        <Input
                          id="current_password"
                          type={showCurrentPassword ? "text" : "password"}
                          value={passwordData.current_password}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-2 top-1/2 -translate-y-1/2"
                          onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        >
                          {showCurrentPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="new_password">New Password</Label>
                      <div className="relative">
                        <Input
                          id="new_password"
                          type={showNewPassword ? "text" : "password"}
                          value={passwordData.new_password}
                          onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="absolute right-2 top-1/2 -translate-y-1/2"
                          onClick={() => setShowNewPassword(!showNewPassword)}
                        >
                          {showNewPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="confirm_password">Confirm New Password</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={passwordData.confirm_password}
                        onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                      />
                    </div>

                    <Button type="submit" disabled={changePasswordMutation.isPending}>
                      {changePasswordMutation.isPending ? "Changing..." : "Change Password"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Notification Settings */}
            <TabsContent value="notifications" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Notification Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleNotificationSubmit} className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Email Notifications</h4>
                          <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                        </div>
                        <Switch
                          checked={notificationSettings.email_notifications}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, email_notifications: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Push Notifications</h4>
                          <p className="text-sm text-muted-foreground">Receive browser notifications</p>
                        </div>
                        <Switch
                          checked={notificationSettings.push_notifications}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, push_notifications: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Mentorship Requests</h4>
                          <p className="text-sm text-muted-foreground">New mentorship requests</p>
                        </div>
                        <Switch
                          checked={notificationSettings.mentorship_requests}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, mentorship_requests: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Roadmap Updates</h4>
                          <p className="text-sm text-muted-foreground">Progress and milestone updates</p>
                        </div>
                        <Switch
                          checked={notificationSettings.roadmap_updates}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, roadmap_updates: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Badge Achievements</h4>
                          <p className="text-sm text-muted-foreground">When you earn new badges</p>
                        </div>
                        <Switch
                          checked={notificationSettings.badge_earned}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, badge_earned: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Weekly Digest</h4>
                          <p className="text-sm text-muted-foreground">Weekly progress summary</p>
                        </div>
                        <Switch
                          checked={notificationSettings.weekly_digest}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, weekly_digest: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Marketing Emails</h4>
                          <p className="text-sm text-muted-foreground">Product updates and tips</p>
                        </div>
                        <Switch
                          checked={notificationSettings.marketing_emails}
                          onCheckedChange={(checked) =>
                            setNotificationSettings(prev => ({ ...prev, marketing_emails: checked }))
                          }
                        />
                      </div>
                    </div>

                    <Button type="submit" disabled={updateNotificationSettingsMutation.isPending}>
                      {updateNotificationSettingsMutation.isPending ? "Saving..." : "Save Preferences"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Privacy Settings */}
            <TabsContent value="privacy" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    Privacy Settings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handlePrivacySubmit} className="space-y-6">
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Profile Visibility</Label>
                        <Select
                          value={privacySettings.profile_visibility}
                          onValueChange={(value) =>
                            setPrivacySettings(prev => ({ ...prev, profile_visibility: value }))
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="public">Public - Visible to everyone</SelectItem>
                            <SelectItem value="mentees">Mentees Only - Visible to your mentees</SelectItem>
                            <SelectItem value="private">Private - Only you can see</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Show Learning Progress</h4>
                          <p className="text-sm text-muted-foreground">Display your roadmap progress publicly</p>
                        </div>
                        <Switch
                          checked={privacySettings.show_progress}
                          onCheckedChange={(checked) =>
                            setPrivacySettings(prev => ({ ...prev, show_progress: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Show Badges & Achievements</h4>
                          <p className="text-sm text-muted-foreground">Display earned badges on your profile</p>
                        </div>
                        <Switch
                          checked={privacySettings.show_badges}
                          onCheckedChange={(checked) =>
                            setPrivacySettings(prev => ({ ...prev, show_badges: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Allow Mentoring Requests</h4>
                          <p className="text-sm text-muted-foreground">Let others request you as a mentor</p>
                        </div>
                        <Switch
                          checked={privacySettings.allow_mentoring}
                          onCheckedChange={(checked) =>
                            setPrivacySettings(prev => ({ ...prev, allow_mentoring: checked }))
                          }
                        />
                      </div>

                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">Data Sharing</h4>
                          <p className="text-sm text-muted-foreground">Share anonymized data for product improvement</p>
                        </div>
                        <Switch
                          checked={privacySettings.data_sharing}
                          onCheckedChange={(checked) =>
                            setPrivacySettings(prev => ({ ...prev, data_sharing: checked }))
                          }
                        />
                      </div>
                    </div>

                    <Button type="submit" disabled={updatePrivacySettingsMutation.isPending}>
                      {updatePrivacySettingsMutation.isPending ? "Saving..." : "Save Privacy Settings"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Appearance Settings */}
            <TabsContent value="appearance" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Palette className="h-5 w-5" />
                    Appearance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label>Theme</Label>
                      <Select value={theme} onValueChange={setTheme}>
                        <SelectTrigger className="w-[200px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="light">Light</SelectItem>
                          <SelectItem value="dark">Dark</SelectItem>
                          <SelectItem value="system">System</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Language</Label>
                      <Select defaultValue="en">
                        <SelectTrigger className="w-[200px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {languages.map((lang) => (
                            <SelectItem key={lang.code} value={lang.code}>
                              {lang.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </DashboardLayout>
  );
}