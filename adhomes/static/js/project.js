/* Project specific Javascript goes here. */

/*
 * Lead forms (home, project, contact page and the side popup) submit in the
 * background and show a short "thank you" toast instead of leaving the page.
 * Without JavaScript they still post normally to the contact page.
 */
(function () {
  const FIELD_LABELS = { name: 'Name', email: 'Email', phone: 'Phone', message: 'Message' }
  let toastTimer = null

  function showToast(text, isError) {
    const toast = document.querySelector('.js-toast')
    if (!toast) return
    toast.querySelector('.js-toast-text').textContent = text
    toast.classList.toggle('-error', !!isError)
    toast.classList.add('is-active')
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => toast.classList.remove('is-active'), isError ? 6000 : 4000)
  }

  function errorText(errors) {
    return Object.entries(errors || {})
      .map(([field, msgs]) => (FIELD_LABELS[field] ? FIELD_LABELS[field] + ': ' : '') + msgs.join(' '))
      .join('\n') || 'Something went wrong. Please try again.'
  }

  document.addEventListener('submit', async (e) => {
    const form = e.target.closest('.js-lead-form')
    if (!form) return
    e.preventDefault()

    const button = form.querySelector('[type="submit"]')
    if (button) button.disabled = true

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        credentials: 'same-origin',
      })
      const data = await res.json()

      if (data.ok) {
        form.reset()
        document.querySelector('.js-requestForm')?.classList.remove('is-active')
        showToast(data.message)
      } else {
        showToast(data.errors ? errorText(data.errors) : data.message, true)
      }
    } catch (err) {
      showToast('Could not send your message. Please check your connection and try again.', true)
    } finally {
      if (button) button.disabled = false
    }
  })

  // A toast rendered already open (flash message after a no-JS redirect)
  // hides itself like any other.
  const initial = document.querySelector('.js-toast.is-active')
  if (initial) {
    toastTimer = setTimeout(() => initial.classList.remove('is-active'), 6000)
  }

  document.addEventListener('click', (e) => {
    if (e.target.closest('.js-toast-close')) {
      document.querySelector('.js-toast')?.classList.remove('is-active')
    }
  })
})()
