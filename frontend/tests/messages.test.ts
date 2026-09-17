import {describe, expect, it} from 'vitest'
import de from '../messages/de.json'
import en from '../messages/en.json'
import {createTranslator} from 'next-intl'

function keys(value: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(value).flatMap(([key, item]) => typeof item === 'object' && item !== null
    ? keys(item as Record<string, unknown>, prefix + key + '.') : [prefix + key]).sort()
}

describe('message catalogues', () => {
  it('has exactly the same keys in both languages', () => expect(keys(de)).toEqual(keys(en)))
  it.each([['de', de], ['en', en]] as const)('formats every %s message', (locale, messages) => {
    const errors: unknown[] = []
    const t = createTranslator({locale, messages, onError: error => errors.push(error)})
    for (const key of keys(messages)) t(key as never, {count: 2, name: "Example"})
    expect(errors).toEqual([])
  })
})
