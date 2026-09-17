import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';
import { displayNameWithLatin } from './utils';

describe('displayNameWithLatin', () => {
  it('returns null without an object or a name', () => {
    expect(displayNameWithLatin(null, 'fullName')).toBeNull();
    expect(
      displayNameWithLatin({ fullNameLatin: 'Ivan' }, 'fullName'),
    ).toBeNull();
  });

  it('returns the plain name when there is no latin twin', () => {
    expect(displayNameWithLatin({ fullName: 'Ivan' }, 'fullName')).toBe('Ivan');
  });

  it('renders the latin twin under the name', () => {
    const { container } = render(
      <>
        {displayNameWithLatin(
          { fullName: 'Іван', fullNameLatin: 'Ivan' },
          'fullName',
        )}
      </>,
    );

    expect(container.textContent).toBe('ІванIvan');
  });
});
