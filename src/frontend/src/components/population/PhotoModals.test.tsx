import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import type { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { RestService } from '@restgenerated/services/RestService';
import { TestProviders } from 'src/testUtils/testProviders';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DocumentPopulationPhotoModal } from './DocumentPopulationPhotoModal';
import { IndividualPhotoModal } from './IndividualPhotoModal';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({ businessArea: 'afghanistan' }),
}));

vi.mock('src/programContext', () => ({
  useProgramContext: () => ({ selectedProgram: { code: 'PRG1' } }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsIndividualsPhotosRetrieve: vi.fn(),
  },
}));

const photosRetrieve =
  RestService.restBusinessAreasProgramsIndividualsPhotosRetrieve as ReturnType<
    typeof vi.fn
  >;

const individual = { id: 'ind-1' } as IndividualDetail;

const photosResponse = (sig: string) => ({
  id: 'ind-1',
  photo: `https://blob/ind.jpg?sig=${sig}`,
  documents: [{ id: 'doc-1', photo: `https://blob/doc.jpg?sig=${sig}` }],
});

const modalImgSrc = () =>
  (
    document.getElementById('modalImg') as HTMLImageElement | null
  )?.getAttribute('src');

describe('photo modals fetch a fresh signed URL on every open', () => {
  beforeEach(() => {
    photosRetrieve.mockReset();
    photosRetrieve
      .mockResolvedValueOnce(photosResponse('first'))
      .mockResolvedValueOnce(photosResponse('second'));
  });

  it('IndividualPhotoModal', async () => {
    render(<IndividualPhotoModal individual={individual} />, {
      wrapper: TestProviders,
    });
    expect(photosRetrieve).not.toHaveBeenCalled();

    fireEvent.click(screen.getByTestId('button-show-photo'));
    await waitFor(() =>
      expect(modalImgSrc()).toBe('https://blob/ind.jpg?sig=first'),
    );

    fireEvent.click(screen.getByTestId('button-cancel'));
    fireEvent.click(screen.getByTestId('button-show-photo'));
    await waitFor(() =>
      expect(modalImgSrc()).toBe('https://blob/ind.jpg?sig=second'),
    );
    expect(photosRetrieve).toHaveBeenCalledTimes(2);
    expect(photosRetrieve).toHaveBeenCalledWith({
      businessAreaSlug: 'afghanistan',
      programCode: 'PRG1',
      id: 'ind-1',
    });
  });

  it('DocumentPopulationPhotoModal', async () => {
    render(
      <DocumentPopulationPhotoModal
        individual={individual}
        documentNumber="123456"
        documentId="doc-1"
      />,
      { wrapper: TestProviders },
    );
    expect(photosRetrieve).not.toHaveBeenCalled();

    fireEvent.click(screen.getByTestId('link-show-photo'));
    await waitFor(() =>
      expect(modalImgSrc()).toBe('https://blob/doc.jpg?sig=first'),
    );

    fireEvent.click(screen.getByTestId('button-cancel'));
    fireEvent.click(screen.getByTestId('link-show-photo'));
    await waitFor(() =>
      expect(modalImgSrc()).toBe('https://blob/doc.jpg?sig=second'),
    );
    expect(photosRetrieve).toHaveBeenCalledTimes(2);
  });
});
