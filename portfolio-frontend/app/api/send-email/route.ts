import { Resend } from 'resend'
import { NextRequest, NextResponse } from 'next/server'

const resend = new Resend(process.env.RESEND_API_KEY)

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, email, subject, message } = body

    // Validierung
    if (!name || !email || !subject || !message) {
      return NextResponse.json(
        { error: 'Alle Felder sind erforderlich' },
        { status: 400 }
      )
    }

    // E-Mail validieren
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Ungültige E-Mail-Adresse' },
        { status: 400 }
      )
    }

    // E-Mail über Resend senden
    const { data, error } = await resend.emails.send({
      from: 'Portfolio Kontaktformular <onboarding@resend.dev>',
      to: ['mannaluca02@gmail.com'],
      replyTo: email,
      subject: `Portfolio Kontakt: ${subject}`,
      html: `
        <h2>Neue Nachricht von deinem Portfolio</h2>
        <p><strong>Name:</strong> ${name}</p>
        <p><strong>E-Mail:</strong> ${email}</p>
        <p><strong>Betreff:</strong> ${subject}</p>
        <hr />
        <h3>Nachricht:</h3>
        <p style="white-space: pre-wrap;">${message}</p>
        <hr />
        <p style="color: #666; font-size: 12px;">
          Diese Nachricht wurde über das Kontaktformular auf lucamanna.ch gesendet.
        </p>
      `,
    })

    if (error) {
      console.error('Resend error:', error)
      return NextResponse.json(
        { error: 'Fehler beim Senden der E-Mail' },
        { status: 500 }
      )
    }

    return NextResponse.json(
      { success: true, messageId: data?.id },
      { status: 200 }
    )
  } catch (error) {
    console.error('Server error:', error)
    return NextResponse.json(
      { error: 'Serverfehler beim Senden der E-Mail' },
      { status: 500 }
    )
  }
}
