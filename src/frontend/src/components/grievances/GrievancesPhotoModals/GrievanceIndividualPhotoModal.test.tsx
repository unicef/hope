import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { RestService } from '@restgenerated/index';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { GrievanceIndividualPhotoModal } from './GrievanceIndividualPhotoModal';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan' }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ selectedProgram: { code: 'PRG1' } }),
}));

vi.mock('@restgenerated/index', () => ({
  RestService: {
    restBusinessAreasProgramsIndividualsPhotosRetrieve: vi.fn(),
  },
}));

const photosRetrieve =
  RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve as ReturnType<
    typeof vi.fn
  >;

const modalImgSrc = () =>
  (
    document.getElementById('modalImg') as HTMLImageElement | null
  )?.getAttribute('src');

describe('GrievanceIndividualPhotoModal', () => {
  beforeEach(() => {
    photosRetrieve.mockReset();
  });

  it('fetches a fresh signed URL when the current photo is opened', async () => {
    photosRetrieve
      .mockResolvedValueOnce({ photo: 'https://blob/ind.jpg?sig=mount' })
      .mockResolvedValueOnce({ photo: 'https://blob/ind.jpg?sig=open' });

    render(<GrievanceIndividualPhotoModal isCurrent individualId="ind-1" />, {
      wrapper: TestProviders,
    });

    const thumbnail = await screen.findByTestId('mini-image');
    expect(photosRetrieve).toHaveBeenCalledTimes(1);

    fireEvent.click(thumbnail);
    await waitFor(() =>
      expect(modalImgSrc()).toBe('https://blob/ind.jpg?sig=open'),
    );
    expect(photosRetrieve).toHaveBeenCalledTimes(2);
  });

  it('uses photoPath for the new value without calling the API', () => {
    render(<GrievanceIndividualPhotoModal photoPath="https://blob/new.jpg" />, {
      wrapper: TestProviders,
    });

    fireEvent.click(screen.getByTestId('mini-image'));
    expect(modalImgSrc()).toBe('https://blob/new.jpg');
    expect(photosRetrieve).not.toHaveBeenCalled();
  });
});
