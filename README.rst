=====================
Viet Nam province API
=====================

Homepage: https://provinces.open-api.vn

This is online tool to let my VietnamProvinces_ library reach more users. VietnamProvinces_ is a Python library, so it can only be used in Python application.
By building an online tool on top of it, I hope to help Viet Nam standard data reach more application developers, easpecially web frontend application, where inclusion of big JSON file is not an optimized option.
In the end, it can help businesses collaborate better (by using the same standard data) and benefit people.


The online tool is built to run on Vercel_ platform, so that I don't have to pay for infrastructure, because this tool is FREE to use.


Development guide
-----------------

If you want to join development, this is what you want to know:

The code consists of two parts:

- Landing page: A static HTML page, built with Zola_. CSS is based on TailwindCSS_.
- API backend: Written in Python_, based on FastAPI_ framework.

Assume that you already install all dependencies.

- To build landing page, run at top level folder:

  .. code-block:: sh

    zola build

- To run the backend, run at top level folder:

  .. code-block:: sh

    uvicorn api.main:app

- If you modify HTML code in landing, chance that you are adding new CSS classes and you don't see update.
  It is because we configure TailwindCSS to delete all unused CSS classes. You need to build TailwindCSS again, let it scan used classes again.
  Run in *front-dev*:

  .. code-block:: sh

    yarn build-tailwind


Credit
------

Brought to you by `Nguyễn Hồng Quân <author_>`_.


.. _vercel: https://vercel.com
.. _zola: https://www.getzola.org/
.. _tailwindcss: https://tailwindcss.com/
.. _python: https://www.python.org/
.. _fastapi: https://fastapi.tiangolo.com/
.. _author: https://quan.hoabinh.vn
.. _VietnamProvinces: https://pypi.org/project/vietnam-provinces/
