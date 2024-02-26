import * as React from 'react';
import { render } from '../../../testUtils/testUtils';
import { ProgramDetails } from './ProgramDetails';
import { fakeProgram } from '../../../../fixtures/programs/fakeProgram';
import { fakeProgramChoices } from '../../../../fixtures/programs/fakeProgramChoices';

describe('components/ProgramDetails', () => {
  it('should render', () => {
    const { container } = render(
      <ProgramDetails program={fakeProgram} choices={fakeProgramChoices} />,
    );
    expect(container).toMatchSnapshot();
  });
});
