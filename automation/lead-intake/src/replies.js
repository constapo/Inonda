// Auto-reply templates per language. Review wording with a native speaker before go-live.
export const REPLIES = {
  en: { subject: "We received your message", body: "Hello {name},\n\nThank you for contacting Inonda. We received your message and will reply within one business day.\n\nInonda — Property Management, Nicosia & Cyprus" },
  el: { subject: "Λάβαμε το μήνυμά σας", body: "Γεια σας {name},\n\nΣας ευχαριστούμε που επικοινωνήσατε με την Inonda. Λάβαμε το μήνυμά σας και θα σας απαντήσουμε εντός μίας εργάσιμης ημέρας.\n\nInonda — Διαχείριση Ακινήτων, Λευκωσία & Κύπρος" },
  he: { subject: "קיבלנו את הודעתך", body: "שלום {name},\n\nתודה שפנית ל-Inonda. קיבלנו את הודעתך ונחזור אליך תוך יום עסקים אחד.\n\nInonda — ניהול נכסים, ניקוסיה וקפריסין" },
  ro: { subject: "Am primit mesajul dvs.", body: "Bună ziua {name},\n\nVă mulțumim că ați contactat Inonda. Am primit mesajul dvs. și vă vom răspunde în decurs de o zi lucrătoare.\n\nInonda — Administrare proprietăți, Nicosia și Cipru" },
  ru: { subject: "Мы получили ваше сообщение", body: "Здравствуйте, {name}!\n\nСпасибо, что обратились в Inonda. Мы получили ваше сообщение и ответим в течение одного рабочего дня.\n\nInonda — управление недвижимостью, Никосия и Кипр" },
  uk: { subject: "Ми отримали ваше повідомлення", body: "Вітаємо, {name}!\n\nДякуємо, що звернулися до Inonda. Ми отримали ваше повідомлення і відповімо протягом одного робочого дня.\n\nInonda — управління нерухомістю, Нікосія та Кіпр" },
};

export function buildReply(lead) {
  const t = REPLIES[lead.language] || REPLIES.en;
  return { to: lead.email, subject: t.subject, text: t.body.replace("{name}", lead.name), dir: lead.language === "he" ? "rtl" : "ltr" };
}
