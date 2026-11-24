import { render, screen } from '@testing-library/react';
import type { ReactElement } from 'react';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { PaymentModuleRoutes } from './PaymentModuleRoutes';
import { PaymentVerificationRoutes } from './PaymentVerificationRoutes';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ baseUrl: 'afghanistan/programs/PRG1' }),
}));

const CurrentPath = (): ReactElement => {
  const { pathname } = useLocation();
  return <div data-cy="current-path">{pathname}</div>;
};

describe('legacy payment module links', () => {
  it('sends an old group link to the payment plan page', () => {
    render(
      <MemoryRouter initialEntries={['/payment-module/groups/G1']}>
        <PaymentModuleRoutes />
        <CurrentPath />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('current-path').textContent).toBe(
      '/afghanistan/programs/PRG1/payment-module/payment-plans/G1',
    );
  });

  it('sends an old follow-up payment plan link to the follow-up payment list page', () => {
    render(
      <MemoryRouter
        initialEntries={['/payment-module/followup-payment-plans/P1']}
      >
        <PaymentModuleRoutes />
        <CurrentPath />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('current-path').textContent).toBe(
      '/afghanistan/programs/PRG1/payment-module/followup-payment-lists/P1',
    );
  });

  it('sends an old cycle payment plan link to the cycle payment list page', () => {
    render(
      <MemoryRouter
        initialEntries={['/payment-module/program-cycles/C1/payment-plans/P1']}
      >
        <PaymentModuleRoutes />
        <CurrentPath />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('current-path').textContent).toBe(
      '/afghanistan/programs/PRG1/payment-module/program-cycles/C1/payment-lists/P1',
    );
  });
});

describe('legacy payment verification links', () => {
  it('sends an old payment plan verification link to the payment list verification page', () => {
    render(
      <MemoryRouter initialEntries={['/payment-verification/payment-plan/P1']}>
        <PaymentVerificationRoutes />
        <CurrentPath />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('current-path').textContent).toBe(
      '/afghanistan/programs/PRG1/payment-verification/payment-list/P1',
    );
  });

  it('sends an old verification payment link to the payment list verification payment page', () => {
    render(
      <MemoryRouter
        initialEntries={[
          '/payment-verification/payment-plan/P1/verification/payment/V1',
        ]}
      >
        <PaymentVerificationRoutes />
        <CurrentPath />
      </MemoryRouter>,
    );

    expect(screen.getByTestId('current-path').textContent).toBe(
      '/afghanistan/programs/PRG1/payment-verification/payment-list/P1/verification/payment/V1',
    );
  });
});
