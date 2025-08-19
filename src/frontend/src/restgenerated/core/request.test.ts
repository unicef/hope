import { describe, it, expect } from 'vitest';
import { processFormData } from './request';

describe('processFormData', () => {
  it('should handle arrays with string values correctly', () => {
    const testData = {
      foo: ['bar', 'baz']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['foo[0]', 'bar'],
      ['foo[1]', 'baz']
    ]);
  });

  it('should handle arrays with number values correctly', () => {
    const testData = {
      numbers: [1, 2, 3]
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['numbers[0]', '1'],
      ['numbers[1]', '2'],
      ['numbers[2]', '3']
    ]);
  });

  it('should handle arrays with boolean values correctly', () => {
    const testData = {
      flags: [true, false, true]
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['flags[0]', 'true'],
      ['flags[1]', 'false'],
      ['flags[2]', 'true']
    ]);
  });

  it('should handle nested objects with arrays correctly', () => {
    const testData = {
      user: {
        tags: ['admin', 'user'],
        preferences: {
          themes: ['dark', 'light']
        }
      }
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['user.tags[0]', 'admin'],
      ['user.tags[1]', 'user'],
      ['user.preferences.themes[0]', 'dark'],
      ['user.preferences.themes[1]', 'light']
    ]);
  });

  it('should handle mixed arrays with different primitive types', () => {
    const testData = {
      mixed: ['string', 42, true, 'another string']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['mixed[0]', 'string'],
      ['mixed[1]', '42'],
      ['mixed[2]', 'true'],
      ['mixed[3]', 'another string']
    ]);
  });

  it('should handle empty arrays correctly', () => {
    const testData = {
      empty: [],
      notEmpty: ['value']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // Empty arrays should be skipped
    expect(entries).toEqual([
      ['not_empty[0]', 'value']
    ]);
  });

  it('should handle null and undefined values correctly', () => {
    const testData = {
      nullValue: null,
      undefinedValue: undefined,
      validValue: 'test'
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // null and undefined values should be skipped
    expect(entries).toEqual([
      ['valid_value', 'test']
    ]);
  });

  it('should handle arrays with null and undefined values correctly', () => {
    const testData = {
      arrayWithNulls: ['valid', null, undefined, 'another valid']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // null and undefined items should be skipped
    expect(entries).toEqual([
      ['array_with_nulls[0]', 'valid'],
      ['array_with_nulls[3]', 'another valid']
    ]);
  });

  it('should handle File objects correctly', () => {
    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const testData = {
      file: file,
      files: [file, new File(['content2'], 'test2.txt', { type: 'text/plain' })]
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toHaveLength(3);
    expect(entries[0][0]).toBe('file');
    expect(entries[0][1]).toBe(file);
    expect(entries[1][0]).toBe('files[0]');
    expect(entries[1][1]).toBe(file);
    expect(entries[2][0]).toBe('files[1]');
    expect(entries[2][1]).toBeInstanceOf(File);
  });

  it('should not iterate over string characters when processing array items', () => {
    // This is the specific bug we're fixing
    const testData = {
      tags: ['hello', 'world']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // Should NOT have entries like tags[0][0], tags[0][1], etc.
    // Should ONLY have tags[0] and tags[1]
    expect(entries).toEqual([
      ['tags[0]', 'hello'],
      ['tags[1]', 'world']
    ]);

    // Verify we don't have character-level entries
    const stringCharEntries = entries.filter(([key]) =>
      key.includes('[0][') || key.includes('[1][')
    );
    expect(stringCharEntries).toHaveLength(0);
  });

  it('should handle the original bug case: {foo: ["bar"]}', () => {
    // This is the exact case described in the issue
    const testData = {
      foo: ['bar']
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // Should have exactly one entry: foo[0] = 'bar'
    expect(entries).toEqual([
      ['foo[0]', 'bar']
    ]);

    // Should NOT have entries like foo[0][0], foo[0][1], foo[0][2] for 'b', 'a', 'r'
    const characterEntries = entries.filter(([key]) =>
      key.match(/foo\[0\]\[\d+\]/)
    );
    expect(characterEntries).toHaveLength(0);
  });

  it('should handle primitive values when called with parentKey', () => {
    // Test direct primitive value processing
    const stringFormData = processFormData('test', undefined, 'stringKey');
    const stringEntries = Array.from(stringFormData.entries());
    expect(stringEntries).toEqual([['stringKey', 'test']]);

    const numberFormData = processFormData(42, undefined, 'numberKey');
    const numberEntries = Array.from(numberFormData.entries());
    expect(numberEntries).toEqual([['numberKey', '42']]);

    const booleanFormData = processFormData(true, undefined, 'booleanKey');
    const booleanEntries = Array.from(booleanFormData.entries());
    expect(booleanEntries).toEqual([['booleanKey', 'true']]);
  });

  it('should handle empty objects correctly', () => {
    const testData = {
      emptyObject: {},
      validValue: 'test'
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    // Empty objects should be skipped
    expect(entries).toEqual([
      ['valid_value', 'test']
    ]);
  });

  it('should handle arrays of objects correctly', () => {
    const testData = {
      items: [
        { name: 'item1', value: 10 },
        { name: 'item2', value: 20 }
      ]
    };

    const formData = processFormData(testData);
    const entries = Array.from(formData.entries());

    expect(entries).toEqual([
      ['items[0].name', 'item1'],
      ['items[0].value', '10'],
      ['items[1].name', 'item2'],
      ['items[1].value', '20']
    ]);
  });
});
