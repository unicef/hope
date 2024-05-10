import { render } from '../../testUtils/testUtils';
import { DocumentSearchField } from '@core/DocumentSearchField';

describe('components/core/DocumentSearchField', () => {
  it('should render', () => {
    const onChangeHandler = () => {};
    const choices = [
      { value: 'Document 1', name: 'Document 1' },
      { value: 'Document 2', name: 'Document 2' },
      { value: 'Document 3', name: 'Document 3' },
      { value: 'Document 4', name: 'Document 4' },
    ];

    const { container } = render(
      <DocumentSearchField
        onChange={onChangeHandler}
        type="Document 1"
        number="123123123"
        choices={choices}
      />,
    );
    expect(container).toMatchSnapshot();
  });
});
