import { render } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mockViewportWidth } from 'src/responsive/testUtils';
import { ProgramStepper } from './ProgramStepper';

const stepsData = [
  { title: 'Details', description: '', dataCy: 'step-details' },
  { title: 'Partners', description: '', dataCy: 'step-partners' },
];

const renderStepper = () =>
  render(<ProgramStepper step={0} setStep={vi.fn()} stepsData={stepsData} />);

const hasLabelsUnderIcons = (container: HTMLElement): boolean =>
  container.querySelector('.MuiStepper-alternativeLabel') !== null;

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('ProgramStepper', () => {
  it('puts labels beside the step icons on desktop', () => {
    mockViewportWidth(1440);
    const { container } = renderStepper();

    expect(hasLabelsUnderIcons(container)).toBe(false);
  });

  it('puts labels under the step icons on mobile', () => {
    mockViewportWidth(375);
    const { container } = renderStepper();

    expect(hasLabelsUnderIcons(container)).toBe(true);
  });
});
