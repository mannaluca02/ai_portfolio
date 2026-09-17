import Home from '@/components/home/Home'
import {setRequestLocale} from 'next-intl/server'

export function generateMetadata({params}: {params: {locale: string}}) {
  return {alternates: {
    canonical: `https://lucamanna.ch/${params.locale}`,
    languages: {de: 'https://lucamanna.ch/de', en: 'https://lucamanna.ch/en', 'x-default': 'https://lucamanna.ch/'},
  }}
}

export default function Page({params}: {params: {locale: string}}) {
  setRequestLocale(params.locale)
  return <Home key={params.locale} />
}
