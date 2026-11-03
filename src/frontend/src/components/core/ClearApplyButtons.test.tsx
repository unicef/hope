import type { ReactElement } from 'react';
import { fireEvent, render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { ClearApplyButtons } from './ClearApplyButtons';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

function renderButtons(extra?: ReactElement) {
  const applyHandler = vi.fn();
  const utils = render(
    <>
      <ClearApplyButtons clearHandler={vi.fn()} applyHandler={applyHandler} />
      <input data-cy="filter-input" />
      {extra}
    </>,
  );
  return { applyHandler, ...utils };
}

describe('ClearApplyButtons', () => {
  it('applies filters on Enter in a filter input', () => {
    const { applyHandler, getByTestId } = renderButtons();
    fireEvent.keyDown(getByTestId('filter-input'), { key: 'Enter' });
    expect(applyHandler).toHaveBeenCalledTimes(1);
  });

  it('ignores Enter in a textarea', () => {
    const { applyHandler, getByTestId } = renderButtons(
      <textarea data-cy="comment" />,
    );
    fireEvent.keyDown(getByTestId('comment'), { key: 'Enter' });
    expect(applyHandler).not.toHaveBeenCalled();
  });

  it('ignores Enter inside a dialog', () => {
    const { applyHandler, getByTestId } = renderButtons(
      <div role="dialog">
        <input data-cy="dialog-input" />
      </div>,
    );
    fireEvent.keyDown(getByTestId('dialog-input'), { key: 'Enter' });
    expect(applyHandler).not.toHaveBeenCalled();
  });
});
