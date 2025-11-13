import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Common
      "common.loading": "Loading...",
      "common.save": "Save",
      "common.cancel": "Cancel",
      "common.delete": "Delete",
      "common.edit": "Edit",
      "common.create": "Create",
      "common.search": "Search",
      "common.filter": "Filter",
      "common.sort": "Sort",
      "common.next": "Next",
      "common.back": "Back",
      "common.close": "Close",
      "common.submit": "Submit",
      "common.reset": "Reset",

      // Navigation
      "nav.dashboard": "Dashboard",
      "nav.community": "Community",
      "nav.roadmaps": "Roadmaps",
      "nav.mentors": "Mentors",
      "nav.notifications": "Notifications",
      "nav.settings": "Settings",

      // Auth
      "auth.signin": "Sign In",
      "auth.signup": "Sign Up",
      "auth.signout": "Sign Out",
      "auth.forgotPassword": "Forgot Password",
      "auth.email": "Email",
      "auth.password": "Password",
      "auth.confirmPassword": "Confirm Password",
      "auth.firstName": "First Name",
      "auth.lastName": "Last Name",
      "auth.rememberMe": "Remember me",

      // Dashboard
      "dashboard.welcome": "Welcome back",
      "dashboard.progress": "Your Progress",
      "dashboard.recentActivity": "Recent Activity",
      "dashboard.quickActions": "Quick Actions",

      // Roadmaps
      "roadmaps.create": "Create Roadmap",
      "roadmaps.myRoadmaps": "My Roadmaps",
      "roadmaps.title": "Title",
      "roadmaps.description": "Description",
      "roadmaps.modules": "Modules",
      "roadmaps.progress": "Progress",
      "roadmaps.completed": "Completed",

      // Mentors
      "mentors.search": "Find Mentors",
      "mentors.request": "Request Mentorship",
      "mentors.skills": "Skills",
      "mentors.experience": "Experience",
      "mentors.rating": "Rating",

      // Settings
      "settings.profile": "Profile",
      "settings.security": "Security",
      "settings.notifications": "Notifications",
      "settings.privacy": "Privacy",
      "settings.appearance": "Appearance",

      // Errors
      "error.generic": "Something went wrong",
      "error.network": "Network error",
      "error.offline": "You're offline",
      "error.online": "Back online",

      // Success
      "success.saved": "Changes saved successfully",
      "success.created": "Created successfully",
      "success.updated": "Updated successfully",
    }
  },
  es: {
    translation: {
      // Common
      "common.loading": "Cargando...",
      "common.save": "Guardar",
      "common.cancel": "Cancelar",
      "common.delete": "Eliminar",
      "common.edit": "Editar",
      "common.create": "Crear",
      "common.search": "Buscar",
      "common.filter": "Filtrar",
      "common.sort": "Ordenar",
      "common.next": "Siguiente",
      "common.back": "Atrás",
      "common.close": "Cerrar",
      "common.submit": "Enviar",
      "common.reset": "Restablecer",

      // Navigation
      "nav.dashboard": "Panel",
      "nav.community": "Comunidad",
      "nav.roadmaps": "Rutas",
      "nav.mentors": "Mentores",
      "nav.notifications": "Notificaciones",
      "nav.settings": "Configuración",

      // Auth
      "auth.signin": "Iniciar Sesión",
      "auth.signup": "Registrarse",
      "auth.signout": "Cerrar Sesión",
      "auth.forgotPassword": "Olvidé mi Contraseña",
      "auth.email": "Correo Electrónico",
      "auth.password": "Contraseña",
      "auth.confirmPassword": "Confirmar Contraseña",
      "auth.firstName": "Nombre",
      "auth.lastName": "Apellido",
      "auth.rememberMe": "Recordarme",

      // Dashboard
      "dashboard.welcome": "Bienvenido de vuelta",
      "dashboard.progress": "Tu Progreso",
      "dashboard.recentActivity": "Actividad Reciente",
      "dashboard.quickActions": "Acciones Rápidas",

      // Roadmaps
      "roadmaps.create": "Crear Ruta",
      "roadmaps.myRoadmaps": "Mis Rutas",
      "roadmaps.title": "Título",
      "roadmaps.description": "Descripción",
      "roadmaps.modules": "Módulos",
      "roadmaps.progress": "Progreso",
      "roadmaps.completed": "Completado",

      // Mentors
      "mentors.search": "Buscar Mentores",
      "mentors.request": "Solicitar Mentoría",
      "mentors.skills": "Habilidades",
      "mentors.experience": "Experiencia",
      "mentors.rating": "Calificación",

      // Settings
      "settings.profile": "Perfil",
      "settings.security": "Seguridad",
      "settings.notifications": "Notificaciones",
      "settings.privacy": "Privacidad",
      "settings.appearance": "Apariencia",

      // Errors
      "error.generic": "Algo salió mal",
      "error.network": "Error de red",
      "error.offline": "Estás desconectado",
      "error.online": "Conexión restablecida",

      // Success
      "success.saved": "Cambios guardados exitosamente",
      "success.created": "Creado exitosamente",
      "success.updated": "Actualizado exitosamente",
    }
  },
  fr: {
    translation: {
      // Common
      "common.loading": "Chargement...",
      "common.save": "Sauvegarder",
      "common.cancel": "Annuler",
      "common.delete": "Supprimer",
      "common.edit": "Modifier",
      "common.create": "Créer",
      "common.search": "Rechercher",
      "common.filter": "Filtrer",
      "common.sort": "Trier",
      "common.next": "Suivant",
      "common.back": "Retour",
      "common.close": "Fermer",
      "common.submit": "Soumettre",
      "common.reset": "Réinitialiser",

      // Navigation
      "nav.dashboard": "Tableau de Bord",
      "nav.community": "Communauté",
      "nav.roadmaps": "Feuilles de Route",
      "nav.mentors": "Mentors",
      "nav.notifications": "Notifications",
      "nav.settings": "Paramètres",

      // Auth
      "auth.signin": "Se Connecter",
      "auth.signup": "S'Inscrire",
      "auth.signout": "Se Déconnecter",
      "auth.forgotPassword": "Mot de Passe Oublié",
      "auth.email": "Email",
      "auth.password": "Mot de Passe",
      "auth.confirmPassword": "Confirmer le Mot de Passe",
      "auth.firstName": "Prénom",
      "auth.lastName": "Nom",
      "auth.rememberMe": "Se Souvenir de Moi",

      // Dashboard
      "dashboard.welcome": "Bienvenue",
      "dashboard.progress": "Votre Progrès",
      "dashboard.recentActivity": "Activité Récente",
      "dashboard.quickActions": "Actions Rapides",

      // Roadmaps
      "roadmaps.create": "Créer une Feuille de Route",
      "roadmaps.myRoadmaps": "Mes Feuilles de Route",
      "roadmaps.title": "Titre",
      "roadmaps.description": "Description",
      "roadmaps.modules": "Modules",
      "roadmaps.progress": "Progrès",
      "roadmaps.completed": "Terminé",

      // Mentors
      "mentors.search": "Trouver des Mentors",
      "mentors.request": "Demander un Mentorat",
      "mentors.skills": "Compétences",
      "mentors.experience": "Expérience",
      "mentors.rating": "Évaluation",

      // Settings
      "settings.profile": "Profil",
      "settings.security": "Sécurité",
      "settings.notifications": "Notifications",
      "settings.privacy": "Confidentialité",
      "settings.appearance": "Apparence",

      // Errors
      "error.generic": "Quelque chose s'est mal passé",
      "error.network": "Erreur réseau",
      "error.offline": "Vous êtes hors ligne",
      "error.online": "De retour en ligne",

      // Success
      "success.saved": "Modifications sauvegardées",
      "success.created": "Créé avec succès",
      "success.updated": "Mis à jour avec succès",
    }
  },
  de: {
    translation: {
      // Common
      "common.loading": "Laden...",
      "common.save": "Speichern",
      "common.cancel": "Abbrechen",
      "common.delete": "Löschen",
      "common.edit": "Bearbeiten",
      "common.create": "Erstellen",
      "common.search": "Suchen",
      "common.filter": "Filtern",
      "common.sort": "Sortieren",
      "common.next": "Weiter",
      "common.back": "Zurück",
      "common.close": "Schließen",
      "common.submit": "Absenden",
      "common.reset": "Zurücksetzen",

      // Navigation
      "nav.dashboard": "Dashboard",
      "nav.community": "Community",
      "nav.roadmaps": "Lernpfade",
      "nav.mentors": "Mentoren",
      "nav.notifications": "Benachrichtigungen",
      "nav.settings": "Einstellungen",

      // Auth
      "auth.signin": "Anmelden",
      "auth.signup": "Registrieren",
      "auth.signout": "Abmelden",
      "auth.forgotPassword": "Passwort vergessen",
      "auth.email": "E-Mail",
      "auth.password": "Passwort",
      "auth.confirmPassword": "Passwort bestätigen",
      "auth.firstName": "Vorname",
      "auth.lastName": "Nachname",
      "auth.rememberMe": "Angemeldet bleiben",

      // Dashboard
      "dashboard.welcome": "Willkommen zurück",
      "dashboard.progress": "Ihr Fortschritt",
      "dashboard.recentActivity": "Kürzliche Aktivitäten",
      "dashboard.quickActions": "Schnellaktionen",

      // Roadmaps
      "roadmaps.create": "Lernpfad erstellen",
      "roadmaps.myRoadmaps": "Meine Lernpfade",
      "roadmaps.title": "Titel",
      "roadmaps.description": "Beschreibung",
      "roadmaps.modules": "Module",
      "roadmaps.progress": "Fortschritt",
      "roadmaps.completed": "Abgeschlossen",

      // Mentors
      "mentors.search": "Mentoren finden",
      "mentors.request": "Mentoring anfragen",
      "mentors.skills": "Fähigkeiten",
      "mentors.experience": "Erfahrung",
      "mentors.rating": "Bewertung",

      // Settings
      "settings.profile": "Profil",
      "settings.security": "Sicherheit",
      "settings.notifications": "Benachrichtigungen",
      "settings.privacy": "Datenschutz",
      "settings.appearance": "Erscheinungsbild",

      // Errors
      "error.generic": "Etwas ist schiefgelaufen",
      "error.network": "Netzwerkfehler",
      "error.offline": "Sie sind offline",
      "error.online": "Wieder online",

      // Success
      "success.saved": "Änderungen gespeichert",
      "success.created": "Erfolgreich erstellt",
      "success.updated": "Erfolgreich aktualisiert",
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',

    interpolation: {
      escapeValue: false, // React already escapes values
    },

    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },

    react: {
      useSuspense: false,
    },
  });

export default i18n;