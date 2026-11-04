import { fireEvent, render, screen } from '@testing-library/react';
import { FileCopy } from '@mui/icons-material';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { mockViewportWidth } from 'src/responsive/testUtils';
import { HeaderIconAction } from './HeaderIconAction';

const renderAction = (onClick = vi.fn()) =>
  render(
    <HeaderIconAction
      icon={<FileCopy />}
      label="Duplicate"
      onClick={onClick}
      dataCy="button-duplicate"
    >
      <button type="button" data-cy="button-duplicate" onClick={onClick}>
        icon
      </button>
    </HeaderIconAction>,
  );

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('HeaderIconAction', () => {
  it('renders the desktop element on desktop', () => {
    mockViewportWidth(1440);
    renderAction();

    expect(screen.getByTestId('button-duplicate').textContent).toBe('icon');
  });

  it('is a labelled button on mobile', () => {
    mockViewportWidth(375);
    const onClick = vi.fn();
    renderAction(onClick);

    const button = screen.getByTestId('button-duplicate');
    expect(button.textContent).toBe('Duplicate');
    fireEvent.click(button);
    expect(onClick).toHaveBeenCalledOnce();
  });
});
