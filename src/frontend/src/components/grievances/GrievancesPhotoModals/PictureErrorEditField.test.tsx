import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { Formik } from 'formik';
import { TestProviders } from 'src/testUtils/testProviders';
import { PictureErrorEditField } from './PictureErrorEditField';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const renderField = (currentPhotoSrc?: string) =>
  render(
    <Formik initialValues={{ photo: null }} onSubmit={vi.fn()}>
      <PictureErrorEditField
        currentPhotoSrc={currentPhotoSrc}
        fieldName="photo"
      />
    </Formik>,
    { wrapper: TestProviders },
  );

describe('PictureErrorEditField', () => {
  it('shows the current photo when one exists', () => {
    renderField('/api/uploads/current.png');
    const img = screen.getByTestId('current-picture') as HTMLImageElement;
    expect(img.src).toContain('/api/uploads/current.png');
    expect(screen.queryByTestId('no-current-picture')).toBeNull();
  });

  it('opens the enlarged photo modal when the current photo is clicked', () => {
    renderField('/api/uploads/current.png');
    // Dialog is closed initially -> the enlarged image is not mounted.
    expect(screen.queryByAltText('photo')).toBeNull();

    fireEvent.click(screen.getByTestId('current-picture'));

    const enlarged = screen.getByAltText('photo') as HTMLImageElement;
    expect(enlarged.src).toContain('/api/uploads/current.png');
  });

  it('shows a placeholder when there is no current photo', () => {
    renderField(undefined);
    expect(screen.getByTestId('no-current-picture')).toBeTruthy();
    expect(screen.queryByTestId('current-picture')).toBeNull();
  });

  it('reveals a remove button after selecting a file and clears it on click', () => {
    renderField('/api/uploads/current.png');
    // No file chosen yet -> no remove button.
    expect(screen.queryByTestId('button-remove-new-photo')).toBeNull();

    const input = screen.getByTestId('file-input') as HTMLInputElement;
    const file = new File(['bytes'], 'new.png', { type: 'image/png' });
    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByTestId('button-remove-new-photo')).toBeTruthy();

    fireEvent.click(screen.getByTestId('button-remove-new-photo'));
    // Cleared: remove button gone and the native input reset.
    expect(screen.queryByTestId('button-remove-new-photo')).toBeNull();
    expect(input.value).toBe('');
  });
});
