=====================
Viet Nam province API
=====================

Homepage: https://provinces.open-api.vn

This is online tool to let my VietnamProvinces_ library reach more users. VietnamProvinces_ is a Python library, so it can only be used in Python application.
By building an online tool on top of it, I hope to help Viet Nam standard data reach more application developers, easpecially web frontend application, where inclusion of big JSON file is not an optimized option.
In the end, it can help businesses collaborate better (by using the same standard data) and benefit people.


The online tool can be self-hosted. The public instance is sponsored by OMZCloud_.


Development guide
-----------------

If you want to join development, this is what you want to know:

The code consists of two parts:

- Landing page: A static HTML page, built with Zola_. CSS is based on TailwindCSS_.
- API backend: Written in Python_, based on FastAPI_ framework.

Assume that you already install all dependencies.

- To build landing page, run at the top-level folder:

  .. code-block:: sh

    zola build

- To run the backend, run at the top-level folder:

  .. code-block:: sh

    uvicorn api.main:app

- When deploying to a live system, we need to route URLs to landing page and the backend. Look into *Deployment/Nginx* for example.

- If you modify HTML code in landing page, chance that you are adding new CSS classes and you don't see update.
  It is because we configure TailwindCSS to delete all unused CSS classes. You need to build TailwindCSS again, let it scan used classes again.
  Doing so by running this command in *front-dev*:

  .. code-block:: sh

    bun run build-tailwind


Credit
------

Brought to you by `Nguyễn Hồng Quân <author_>`_.


.. _zola: https://www.getzola.org/
.. _tailwindcss: https://tailwindcss.com/
.. _python: https://www.python.org/
.. _fastapi: https://fastapi.tiangolo.com/
.. _author: https://quan.hoabinh.vn
.. _VietnamProvinces: https://pypi.org/project/vietnam-provinces/
.. _OMZCloud: https://omzcloud.vn/
