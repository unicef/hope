import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { RuleNameWithDescription } from './RuleNameWithDescription';

describe('RuleNameWithDescription', () => {
  it('shows the description on hover', async () => {
    render(
      <RuleNameWithDescription
        name="Formula A"
        description="Gives 10 USD per member"
      />,
    );
    fireEvent.mouseOver(screen.getByText('Formula A'));
    expect(await screen.findByText('Gives 10 USD per member')).toBeTruthy();
  });

  it('renders only the name when there is no description', async () => {
    render(<RuleNameWithDescription name="Formula B" description="" />);
    const name = screen.getByText('Formula B');
    expect(name.getAttribute('aria-label')).toBeNull();
    fireEvent.mouseOver(name);
    await new Promise((resolve) => setTimeout(resolve, 200));
    expect(screen.queryByRole('tooltip')).toBeNull();
  });
});
