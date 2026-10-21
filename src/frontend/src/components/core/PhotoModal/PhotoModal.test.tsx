import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { TestProviders } from 'src/testUtils/testProviders';
import PhotoModal from './PhotoModal';

describe('PhotoModal', () => {
  it('link variant opens the dialog on click without a router context', () => {
    // Rendered deliberately without a Router: the link variant used to be a
    // react-router <Link to={null}>, which throws on click in react-router >= 7.18.3.
    render(
      <PhotoModal
        variant="link"
        linkText="123456"
        src="http://example.com/photo.jpg"
      />,
      { wrapper: TestProviders },
    );

    const link = screen.getByTestId('link-show-photo');
    expect(link.tagName).toBe('A');
    expect(link.textContent).toBe('123456');
    expect(screen.queryByTestId('dialog-root')).toBeNull();

    expect(() => fireEvent.click(link)).not.toThrow();

    expect(screen.getByTestId('dialog-root')).toBeTruthy();
    expect(screen.getByText('Photo')).toBeTruthy();
  });

  it('calls onOpen when the dialog is opened', () => {
    const onOpen = vi.fn();
    render(<PhotoModal variant="button" onOpen={onOpen} />, {
      wrapper: TestProviders,
    });

    expect(onOpen).not.toHaveBeenCalled();
    fireEvent.click(screen.getByTestId('button-show-photo'));
    expect(onOpen).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('dialog-root')).toBeTruthy();
  });
});
