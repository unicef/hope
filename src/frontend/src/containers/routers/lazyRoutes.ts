import { lazy } from 'react';

export const LazyAccountabilityRoutes = lazy(() =>
  import('./AccountabilityRoutes').then((m) => ({
    default: m.AccountabilityRoutes,
  })),
);
export const LazyGrievanceRoutes = lazy(() =>
  import('./GrievanceRoutes').then((m) => ({ default: m.GrievanceRoutes })),
);
export const LazyPaymentModuleRoutes = lazy(() =>
  import('./PaymentModuleRoutes').then((m) => ({
    default: m.PaymentModuleRoutes,
  })),
);
export const LazyPaymentVerificationRoutes = lazy(() =>
  import('./PaymentVerificationRoutes').then((m) => ({
    default: m.PaymentVerificationRoutes,
  })),
);
export const LazyPopulationRoutes = lazy(() =>
  import('./PopulationRoutes').then((m) => ({ default: m.PopulationRoutes })),
);
export const LazyProgramRoutes = lazy(() =>
  import('./ProgramRoutes').then((m) => ({ default: m.ProgramRoutes })),
);
export const LazyRegistrationRoutes = lazy(() =>
  import('./RegistrationRoutes').then((m) => ({
    default: m.RegistrationRoutes,
  })),
);
export const LazyTargetingRoutes = lazy(() =>
  import('./TargetingRoutes').then((m) => ({ default: m.TargetingRoutes })),
);
