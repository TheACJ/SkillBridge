import { test, expect } from '@playwright/test';

test.describe('User Journey E2E Tests', () => {
  test('Complete user flow: Signup → Roadmap Create → Mentor Search → Match → Community Post → Notifications', async ({ page }) => {
    // Generate unique test data
    const timestamp = Date.now();
    const testEmail = `testuser${timestamp}@example.com`;
    const testPassword = 'TestPassword123!';
    const testFirstName = 'Test';
    const testLastName = 'User';

    // Step 1: Signup Flow
    await test.step('User Registration', async () => {
      await page.goto('/');
      await page.getByRole('link', { name: /sign up/i }).click();

      // Fill signup form
      await page.getByLabel(/first name/i).fill(testFirstName);
      await page.getByLabel(/last name/i).fill(testLastName);
      await page.getByLabel(/email/i).fill(testEmail);
      await page.getByLabel(/password/i).fill(testPassword);
      await page.getByLabel(/confirm password/i).fill(testPassword);

      // Select role
      await page.getByRole('button', { name: /learner/i }).click();

      // Submit form
      await page.getByRole('button', { name: /create account/i }).click();

      // Should redirect to dashboard
      await expect(page).toHaveURL(/.*\/dashboard/);
      await expect(page.getByText(`Welcome back, ${testFirstName}`)).toBeVisible();
    });

    // Step 2: Roadmap Creation Flow
    await test.step('Roadmap Creation', async () => {
      // Navigate to roadmap creation
      await page.getByRole('link', { name: /roadmaps/i }).click();
      await page.getByRole('button', { name: /create roadmap/i }).click();

      // Complete quiz
      await page.getByText('Become a full-stack web developer').click();
      await page.getByRole('button', { name: /next/i }).click();

      await page.getByText('Intermediate').click();
      await page.getByRole('button', { name: /next/i }).click();

      await page.getByText('20-30 hours').click();
      await page.getByRole('button', { name: /next/i }).click();

      await page.getByText('Hands-on projects').click();
      await page.getByRole('button', { name: /create roadmap/i }).click();

      // Should redirect to roadmap viewer
      await expect(page).toHaveURL(/.*\/roadmaps\/\d+/);
      await expect(page.getByText(/learning modules/i)).toBeVisible();
    });

    // Step 3: Mentor Search Flow
    await test.step('Mentor Search', async () => {
      await page.getByRole('link', { name: /mentors/i }).click();

      // Search for mentors
      await page.getByPlaceholder(/search mentors/i).fill('Python');
      await page.getByRole('button', { name: /python/i }).click();

      // Should show mentor results
      await expect(page.getByText(/mentors found/i)).toBeVisible();
    });

    // Step 4: Mentor Request Flow
    await test.step('Mentor Request', async () => {
      // Click on first mentor card
      const mentorCard = page.locator('[data-testid="mentor-card"]').first();
      await mentorCard.click();

      // Fill request form
      await page.getByLabel(/learning goals/i).fill('I want to learn Python for web development');
      await page.getByLabel(/availability/i).selectOption('flexible');
      await page.getByLabel(/personal message/i).fill('Hi, I am interested in learning Python from you.');

      // Submit request
      await page.getByRole('button', { name: /send request/i }).click();

      // Should show success message
      await expect(page.getByText(/request sent/i)).toBeVisible();
    });

    // Step 5: Community Post Flow
    await test.step('Community Post', async () => {
      await page.getByRole('link', { name: /community/i }).click();

      // Create a new post
      await page.getByRole('button', { name: /new post/i }).click();
      await page.getByLabel(/title/i).fill('Test Post: Learning Python');
      await page.getByLabel(/content/i).fill('This is a test post about learning Python. Any tips?');
      await page.getByRole('button', { name: /post/i }).click();

      // Should show the new post
      await expect(page.getByText('Test Post: Learning Python')).toBeVisible();
    });

    // Step 6: Notifications Flow
    await test.step('Notifications Check', async () => {
      await page.getByRole('link', { name: /notifications/i }).click();

      // Should show notifications
      await expect(page.getByText(/notifications/i)).toBeVisible();

      // Check for unread notifications
      const unreadBadge = page.locator('[data-testid="unread-count"]');
      if (await unreadBadge.isVisible()) {
        await expect(unreadBadge).toContainText(/\d+/);
      }
    });

    // Step 7: Settings Flow
    await test.step('Settings Access', async () => {
      await page.getByRole('link', { name: /settings/i }).click();

      // Should show settings tabs
      await expect(page.getByRole('tab', { name: /profile/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /security/i })).toBeVisible();
      await expect(page.getByRole('tab', { name: /notifications/i })).toBeVisible();
    });
  });

  test('Authentication Flow', async ({ page }) => {
    await test.step('Sign In', async () => {
      await page.goto('/');
      await page.getByRole('link', { name: /sign in/i }).click();

      await page.getByLabel(/email/i).fill('existing@example.com');
      await page.getByLabel(/password/i).fill('password123');
      await page.getByRole('button', { name: /login/i }).click();

      // Should redirect or show error
      await expect(page).toHaveURL(/.*(\/dashboard|\/signin)/);
    });

    await test.step('Forgot Password', async () => {
      await page.getByRole('link', { name: /forgot password/i }).click();
      await page.getByLabel(/email/i).fill('test@example.com');
      await page.getByRole('button', { name: /reset password/i }).click();

      await expect(page.getByText(/reset link sent/i)).toBeVisible();
    });
  });

  test('Responsive Design', async ({ page, isMobile }) => {
    await page.goto('/');

    if (isMobile) {
      // Check mobile navigation
      await page.getByRole('button', { name: /menu/i }).click();
      await expect(page.getByRole('navigation')).toBeVisible();
    } else {
      // Check desktop navigation
      await expect(page.getByRole('navigation')).toBeVisible();
    }
  });

  test('Error Handling', async ({ page }) => {
    await test.step('404 Page', async () => {
      await page.goto('/nonexistent-page');
      await expect(page.getByText(/page not found/i)).toBeVisible();
    });

    await test.step('Network Error Simulation', async () => {
      // This would require setting up network interception
      // For now, just check that error boundaries work
      await page.goto('/');
      // Simulate network failure by blocking API calls
      await page.route('**/api/**', route => route.abort());
      await page.reload();
      // App should still render with offline indicator
      await expect(page.getByText(/offline/i)).toBeVisible({ timeout: 10000 });
    });
  });
});